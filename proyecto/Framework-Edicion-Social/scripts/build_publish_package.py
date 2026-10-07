#!/usr/bin/env python3
"""Build a fail-closed multichannel package from one approved SDR master.

The command is intentionally read-only unless ``--write`` is supplied. A
ready package is emitted only after revalidating every file-backed contract:
the platform master, both approval receipts, the full SDR profile report, the
platform catalog, and a sealed content-lock inventory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import shutil
import stat
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
FRAMEWORK = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from approval_receipt import (  # noqa: E402
    ApprovalReceiptError,
    load_json as load_receipt_json,
    parse_rfc3339,
    resolve_artifact_path,
    verify_receipt,
)
from check_master_profile import (  # noqa: E402
    MasterProfileError,
    evaluate_profile,
    load_profile,
)
from check_platform_delivery import (  # noqa: E402
    DeliveryCheckError,
    parse_ffprobe,
    run_ffprobe,
)
from plan_platform_derivatives import (  # noqa: E402
    DEFAULT_CATALOG,
    PlatformPlanError,
    _parse_targets,
    build_plan,
    document_payload_sha256,
    load_catalog,
    read_json,
    seal_document,
    validate_catalog_document,
    validate_master,
    verify_document_binding,
)
from schema_validation import load_json as load_schema_json  # noqa: E402
from schema_validation import validate_document  # noqa: E402


PACKAGE_SCHEMA = FRAMEWORK / "schemas/publish-package.schema.json"
ADAPTATION_SCHEMA = FRAMEWORK / "schemas/platform-adaptation.schema.json"
BRIEF_SCHEMA = FRAMEWORK / "schemas/package-brief.schema.json"
CONTENT_LOCK_SCHEMA = FRAMEWORK / "schemas/content-lock-evidence.schema.json"
SOCIAL_PROFILE_PATH = FRAMEWORK / "master-profiles/social-delivery-sdr-001.json"
EDITORIAL_PROFILE_PATH = FRAMEWORK / "master-profiles/editorial-mezzanine-hdr-001.json"
SOCIAL_ROLE = "social_delivery_master"
SOCIAL_PROFILE = "MASTER-PROFILE-SOCIAL-SDR-001"
EDITORIAL_ROLE = "editorial_mezzanine"
EDITORIAL_PROFILE = "MASTER-PROFILE-EDITORIAL-HDR-001"
SAFE_ID = re.compile(r"[^A-Z0-9-]+")
CONTENT_LOCK_ROLES = {"project", "cut_plan", "audio_mix"}
REPORT_FIELDS = {
    "schema_version", "profile_id", "profile_version", "profile_sha256",
    "artifact_role", "color_intent", "media_path", "media_sha256",
    "source_sha256", "inspected_at", "technical_status", "loudness_status",
    "lineage_status", "tone_map_status", "visual_review_status",
    "profile_status", "visual_review_required", "publication_ready",
    "status_notice", "metadata", "probe_evidence", "loudness",
    "loudness_evidence", "approval_receipt_verification",
    "source_profile_verification", "source_probe_evidence",
    "tone_map_evidence", "visual_review", "findings",
}
PROBE_EVIDENCE_FIELDS = {
    "schema_version", "kind", "authoritative", "media_sha256",
    "captured_at", "tool",
}
LOUDNESS_EVIDENCE_FIELDS = {
    "schema_version", "kind", "authoritative", "media_sha256",
    "measured_at", "tool",
}


class PublishPackageError(ValueError):
    """Publication inputs are incomplete, inconsistent, or unsafe."""


def _slug(value):
    result = SAFE_ID.sub("-", str(value).upper()).strip("-")
    if not result:
        raise PublishPackageError("cannot create a package id from an empty value")
    return result


def _safe_fragment(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", value):
        raise PublishPackageError(f"{label} is not a safe path fragment: {value!r}")
    return value


def _same_number(actual, expected, tolerance=0.01):
    try:
        left = float(actual)
        right = float(expected)
    except (TypeError, ValueError):
        return False
    return math.isfinite(left) and math.isfinite(right) and abs(left - right) <= tolerance


def _validate_past_timestamp(value, label):
    parsed = parse_rfc3339(value)
    if parsed is None:
        raise PublishPackageError(f"{label} must be an RFC 3339 timestamp")
    if parsed > datetime.now(timezone.utc):
        raise PublishPackageError(f"{label} cannot be in the future")
    return parsed


def _lexical_absolute(path):
    return Path(os.path.abspath(os.fspath(Path(path).expanduser())))


def _validate_clean_path(value, label, *, relative=False):
    if not isinstance(value, (str, os.PathLike)):
        raise PublishPackageError(f"{label} must be a string or path")
    raw = os.fspath(value)
    if not isinstance(raw, str) or not raw.strip():
        raise PublishPackageError(f"{label} must be a non-empty text path")
    if "\x00" in raw:
        raise PublishPackageError(f"{label} cannot contain a NUL byte")
    parts = raw.replace("\\", "/").split("/")
    if any(part in {".", ".."} for part in parts):
        raise PublishPackageError(f"{label} cannot contain . or .. path segments")
    if relative and Path(raw).is_absolute():
        raise PublishPackageError(f"{label} must be relative")
    return raw


def _assert_no_symlink_chain(path, label):
    """Reject symlinks before resolving them, including broken leaf links."""
    if not isinstance(path, (str, os.PathLike)) or not os.fspath(path).strip():
        raise PublishPackageError(f"{label} path must be a non-empty string or path")
    absolute = _lexical_absolute(path)
    cursor = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        cursor = cursor / part
        if cursor.is_symlink():
            # Stable aliases built into macOS. Descendants are still checked.
            if str(cursor) in {"/var", "/tmp"}:
                continue
            raise PublishPackageError(f"{label} may not traverse a symlink: {cursor}")
    return absolute


def _regular_non_symlink(path, label):
    raw = _assert_no_symlink_chain(path, label)
    try:
        resolved = raw.resolve(strict=True)
    except (FileNotFoundError, RuntimeError) as error:
        raise PublishPackageError(f"{label} does not exist: {raw}") from error
    try:
        mode = os.lstat(resolved).st_mode
    except OSError as error:
        raise PublishPackageError(f"{label} cannot be inspected: {resolved}") from error
    if stat.S_ISLNK(mode):
        raise PublishPackageError(f"{label} cannot be a symlink: {resolved}")
    if not stat.S_ISREG(mode):
        raise PublishPackageError(f"{label} must be a regular file: {resolved}")
    return resolved


def _artifact_non_symlink(path, label):
    raw = _assert_no_symlink_chain(path, label)
    try:
        resolved = raw.resolve(strict=True)
    except (FileNotFoundError, RuntimeError) as error:
        raise PublishPackageError(f"{label} does not exist: {raw}") from error
    try:
        mode = os.lstat(resolved).st_mode
    except OSError as error:
        raise PublishPackageError(f"{label} cannot be inspected: {resolved}") from error
    if stat.S_ISLNK(mode):
        raise PublishPackageError(f"{label} cannot be a symlink: {resolved}")
    if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
        raise PublishPackageError(f"{label} must be a regular file or directory: {resolved}")
    return resolved


def _inside(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _snapshot_file(path, label, *, capture_bytes=False):
    """Read/hash one immutable regular-file handle and retain identity metadata.

    JSON callers opt in to retaining the exact bytes they parse. Media files are
    streamed through the digest without being duplicated in memory.
    """
    resolved = _regular_non_symlink(path, label)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(resolved, flags)
    except OSError as error:
        raise PublishPackageError(f"{label} cannot be opened safely: {resolved}: {error}") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise PublishPackageError(f"{label} must be a regular file: {resolved}")
        chunks = [] if capture_bytes else None
        digest = hashlib.sha256()
        total = 0
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            if chunks is not None:
                chunks.append(chunk)
            digest.update(chunk)
            total += len(chunk)
        after = os.fstat(descriptor)
        identity = (before.st_dev, before.st_ino)
        if identity != (after.st_dev, after.st_ino) or (
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) != (
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ) or total != after.st_size:
            raise PublishPackageError(f"{label} changed while it was being read: {resolved}")
        return {
            "path": resolved,
            "bytes": b"".join(chunks) if chunks is not None else None,
            "sha256": digest.hexdigest(),
            "size_bytes": total,
            "identity": identity,
            "mtime_ns": after.st_mtime_ns,
            "ctime_ns": after.st_ctime_ns,
        }
    except PublishPackageError:
        raise
    except OSError as error:
        raise PublishPackageError(f"{label} cannot be read safely: {resolved}: {error}") from error
    finally:
        os.close(descriptor)


def _snapshot_json(path, label):
    snapshot = _snapshot_file(path, label, capture_bytes=True)
    try:
        text = snapshot["bytes"].decode("utf-8")
        snapshot["document"] = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PublishPackageError(f"invalid {label} at {snapshot['path']}: {error}") from error
    return snapshot


def _load_bound_json(path, supplied, label):
    snapshot = _snapshot_json(path, label)
    if snapshot["document"] != supplied:
        raise PublishPackageError(f"in-memory {label} differs from its declared file")
    return snapshot


def _assert_snapshot_unchanged(snapshot, label):
    current = _snapshot_file(snapshot["path"], label)
    for field in ("sha256", "size_bytes", "identity", "mtime_ns", "ctime_ns"):
        if current[field] != snapshot[field]:
            raise PublishPackageError(f"{label} changed before atomic commit")
    return current


def _probe_media(path, label):
    """Production probe boundary; tests monkeypatch this private function only."""
    try:
        return parse_ffprobe(run_ffprobe(path))
    except (DeliveryCheckError, OSError, TypeError, ValueError) as error:
        raise PublishPackageError(f"{label} ffprobe failed: {error}") from error


def validate_media_facts(facts, master):
    """Bind the declared master manifest to independently probed media facts."""
    if not isinstance(facts, dict):
        raise PublishPackageError("master media facts must be a JSON object")
    technical = master["technical"]
    comparisons = {
        "width": (facts.get("width"), technical["width"]),
        "height": (facts.get("height"), technical["height"]),
        "aspect_ratio": (facts.get("aspect_ratio"), technical["aspect_ratio"]),
        "container": (facts.get("container"), technical["container"]),
        "video_codec": (facts.get("video_codec"), technical["video_codec"]),
        "pixel_format": (facts.get("pixel_format"), technical["pixel_format"]),
        "audio_codec": (facts.get("audio_codec"), technical["audio_codec"]),
        "audio_sample_rate_hz": (
            facts.get("audio_sample_rate_hz"), technical["audio_sample_rate_hz"]
        ),
        "color_space": (facts.get("color_space"), technical["color_space"]),
    }
    mismatches = []
    for field, (actual, expected) in comparisons.items():
        if actual is None or str(actual).lower() != str(expected).lower():
            mismatches.append(f"{field}={actual!r}, manifest={expected!r}")
    if not _same_number(facts.get("fps"), technical["fps"], tolerance=0.02):
        mismatches.append(f"fps={facts.get('fps')!r}, manifest={technical['fps']!r}")
    if not _same_number(
        facts.get("duration_seconds"), technical["duration_seconds"], tolerance=0.08
    ):
        mismatches.append(
            "duration_seconds="
            f"{facts.get('duration_seconds')!r}, manifest={technical['duration_seconds']!r}"
        )
    if mismatches:
        raise PublishPackageError("master media does not match its manifest: " + "; ".join(mismatches))


def validate_source_receipt(receipt, receipt_path, master_media, master):
    report = verify_receipt(receipt, receipt_path=receipt_path, artifact_override=master_media)
    if not report.get("usable_as_approval"):
        details = "; ".join(report.get("errors") or []) or "receipt is not usable"
        raise PublishPackageError(f"SDR approval receipt failed: {details}")
    artifact = receipt["artifact"]
    decision = receipt["decision"]
    _validate_clean_path(artifact.get("path"), "SDR receipt artifact path")
    if artifact["media_role"] != SOCIAL_ROLE:
        raise PublishPackageError(f"approval receipt must bind media_role={SOCIAL_ROLE}")
    if artifact["profile_id"] != SOCIAL_PROFILE:
        raise PublishPackageError(f"approval receipt must bind profile_id={SOCIAL_PROFILE}")
    if receipt["project_id"] != master["project_id"] or receipt["video_id"] != master["video_id"]:
        raise PublishPackageError("approval receipt project/video does not match platform master")
    if decision["scope"]["whole_artifact"] is not True or decision["scope"]["approved_layers"]:
        raise PublishPackageError("publication requires whole-artifact SDR approval")
    approval = master["approval"]
    if approval["status"] == "approved" and (
        approval["approved_by"] != decision["approver"]
        or approval["approved_at"] != decision["decided_at"]
    ):
        raise PublishPackageError(
            "platform master approval provenance does not match the sealed SDR receipt"
        )
    return report


def _validate_editorial_receipt(receipt, receipt_path, master):
    artifact_contract = receipt.get("artifact") if isinstance(receipt, dict) else None
    if not isinstance(artifact_contract, dict):
        raise PublishPackageError("editorial approval receipt artifact must be an object")
    _validate_clean_path(artifact_contract.get("path"), "editorial receipt artifact path")
    artifact_candidate = resolve_artifact_path(receipt, receipt_path=receipt_path)
    if artifact_candidate is None:
        raise PublishPackageError("editorial approval receipt has no artifact path")
    source_media = _regular_non_symlink(artifact_candidate, "approved editorial source")
    report = verify_receipt(receipt, receipt_path=receipt_path, artifact_override=source_media)
    if not report.get("usable_as_approval"):
        details = "; ".join(report.get("errors") or []) or "receipt is not usable"
        raise PublishPackageError(f"editorial approval receipt failed: {details}")
    artifact = receipt["artifact"]
    decision = receipt["decision"]
    if artifact.get("media_role") != EDITORIAL_ROLE:
        raise PublishPackageError(f"editorial receipt must bind media_role={EDITORIAL_ROLE}")
    if artifact.get("profile_id") != EDITORIAL_PROFILE:
        raise PublishPackageError(f"editorial receipt must bind profile_id={EDITORIAL_PROFILE}")
    if receipt.get("project_id") != master["project_id"] or receipt.get("video_id") != master["video_id"]:
        raise PublishPackageError("editorial receipt project/video does not match platform master")
    scope = decision.get("scope", {})
    if scope.get("whole_artifact") is not True or scope.get("approved_layers"):
        raise PublishPackageError("SDR lineage requires whole-artifact editorial approval")
    return source_media, report


def _validate_evidence_summary(evidence, expected_fields, *, kind, hash_value, time_field, label):
    if not isinstance(evidence, dict) or set(evidence) != expected_fields:
        raise PublishPackageError(f"{label} fields must be exactly {sorted(expected_fields)}")
    expected = {
        "schema_version": "1.0.0",
        "kind": kind,
        "authoritative": True,
        "media_sha256": hash_value,
    }
    for field, value in expected.items():
        if evidence.get(field) != value:
            raise PublishPackageError(f"{label} {field} must equal {value!r}")
    _validate_past_timestamp(evidence.get(time_field), f"{label} {time_field}")
    if not isinstance(evidence.get("tool"), str) or not evidence["tool"].strip():
        raise PublishPackageError(f"{label} tool must be non-empty")


def _normalized_replay(report):
    value = copy.deepcopy(report)
    value.pop("inspected_at", None)
    value.pop("media_path", None)
    nested = value.get("source_profile_verification")
    if isinstance(nested, dict):
        nested.pop("inspected_at", None)
        nested.pop("media_path", None)
    return value


def validate_master_profile_report(
    report,
    master_media_hash,
    master,
    *,
    master_media,
    report_path,
    source_receipt,
    source_receipt_path,
):
    """Replay the complete trusted SDR evaluation from file-backed evidence."""
    del report_path  # Binding to this file is enforced by build_package.
    if not isinstance(report, dict) or set(report) != REPORT_FIELDS:
        raise PublishPackageError(
            "master profile report fields must be exactly " + str(sorted(REPORT_FIELDS))
        )
    if report.get("schema_version") != "1.0.0":
        raise PublishPackageError("master profile report has unsupported schema_version")
    inspected_at = _validate_past_timestamp(report.get("inspected_at"), "profile inspected_at")
    _validate_clean_path(report.get("media_path"), "profile report media_path")
    report_media = _regular_non_symlink(report.get("media_path"), "profile report media_path")
    if report_media != master_media:
        raise PublishPackageError("master profile report media_path does not resolve to the SDR master")
    media_facts = _probe_media(master_media, "SDR master")
    validate_media_facts(media_facts, master)
    if report.get("metadata") != media_facts:
        raise PublishPackageError("master profile report metadata differs from the fresh media probe")

    _validate_evidence_summary(
        report.get("probe_evidence"), PROBE_EVIDENCE_FIELDS,
        kind="ffprobe_capture", hash_value=master_media_hash,
        time_field="captured_at", label="SDR probe evidence",
    )
    _validate_evidence_summary(
        report.get("loudness_evidence"), LOUDNESS_EVIDENCE_FIELDS,
        kind="loudness_measurement", hash_value=master_media_hash,
        time_field="measured_at", label="SDR loudness evidence",
    )
    source_media, source_receipt_report = _validate_editorial_receipt(
        source_receipt, source_receipt_path, master
    )
    source_hash = source_receipt_report["actual_artifact_sha256"]
    nested = report.get("source_profile_verification")
    if not isinstance(nested, dict) or set(nested) != REPORT_FIELDS:
        raise PublishPackageError("master profile report lacks a complete source profile verification")
    _validate_past_timestamp(nested.get("inspected_at"), "source profile inspected_at")
    _validate_clean_path(nested.get("media_path"), "source profile media_path")
    nested_media = _regular_non_symlink(nested.get("media_path"), "source profile media_path")
    if nested_media != source_media:
        raise PublishPackageError("source profile media_path does not resolve to the approved editorial source")
    actual_source_facts = _probe_media(source_media, "editorial source")
    if not isinstance(actual_source_facts, dict):
        raise PublishPackageError("editorial source media facts must be a JSON object")
    if nested.get("metadata") != actual_source_facts:
        raise PublishPackageError(
            "source profile metadata differs from the fresh editorial media probe"
        )
    _validate_evidence_summary(
        nested.get("probe_evidence"), PROBE_EVIDENCE_FIELDS,
        kind="ffprobe_capture", hash_value=source_hash,
        time_field="captured_at", label="editorial probe evidence",
    )

    try:
        social_profile = load_profile(SOCIAL_PROFILE_PATH)
        editorial_profile = load_profile(EDITORIAL_PROFILE_PATH)
        replay = evaluate_profile(
            social_profile,
            media_facts,
            media_path=master_media,
            media_sha256=master_media_hash,
            probe_authoritative=True,
            probe_evidence=report["probe_evidence"],
            loudness=report.get("loudness"),
            loudness_authoritative=True,
            loudness_evidence=report["loudness_evidence"],
            approval_receipt=source_receipt,
            approval_receipt_path=source_receipt_path,
            source_master=source_media,
            source_profile=editorial_profile,
            source_metadata=actual_source_facts,
            source_probe_authoritative=True,
            source_probe_evidence=nested["probe_evidence"],
            expected_project_id=master["project_id"],
            expected_video_id=master["video_id"],
            tone_map_evidence=report.get("tone_map_evidence"),
            visual_review=report.get("visual_review"),
        )
    except (ApprovalReceiptError, MasterProfileError, KeyError, TypeError, ValueError) as error:
        raise PublishPackageError(f"master profile report replay failed: {error}") from error
    if _normalized_replay(report) != _normalized_replay(replay):
        raise PublishPackageError(
            "master profile report does not match a fresh replay of its trusted evidence"
        )
    if not report.get("publication_ready"):
        raise PublishPackageError("master profile report is not publication-ready")
    if any(item.get("severity") == "error" for item in report.get("findings", [])):
        raise PublishPackageError("master profile report contains error findings")
    for evidence, time_field in (
        (report["probe_evidence"], "captured_at"),
        (report["loudness_evidence"], "measured_at"),
    ):
        if _validate_past_timestamp(evidence[time_field], time_field) > inspected_at:
            raise PublishPackageError(f"{time_field} cannot follow profile inspected_at")
    nested_inspected = _validate_past_timestamp(
        nested["inspected_at"], "source profile inspected_at"
    )
    if _validate_past_timestamp(
        nested["probe_evidence"]["captured_at"], "source probe captured_at"
    ) > nested_inspected:
        raise PublishPackageError("source probe captured_at cannot follow source profile inspected_at")
    return replay, source_media, source_receipt_report


def fingerprint_content_artifact(path, label="content-lock artifact"):
    """Fingerprint one regular file or a deterministic, symlink-free directory tree."""
    resolved = _artifact_non_symlink(path, label)
    try:
        root_mode = os.lstat(resolved).st_mode
    except OSError as error:
        raise PublishPackageError(f"{label} cannot be inspected: {resolved}: {error}") from error
    if stat.S_ISLNK(root_mode):
        raise PublishPackageError(f"{label} cannot be a symlink: {resolved}")
    if stat.S_ISREG(root_mode):
        snapshot = _snapshot_file(resolved, label)
        return {
            "kind": "file",
            "sha256": snapshot["sha256"],
            "size_bytes": snapshot["size_bytes"],
        }
    if not stat.S_ISDIR(root_mode):
        raise PublishPackageError(f"{label} must be a regular file or directory: {resolved}")

    files = []
    directories = []
    total = 0

    def visit(directory):
        nonlocal total
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda entry: entry.name)
        except OSError as error:
            raise PublishPackageError(
                f"{label} directory cannot be read completely: {directory}: {error}"
            ) from error
        for entry in entries:
            candidate = Path(entry.path)
            try:
                mode = os.lstat(candidate).st_mode
            except OSError as error:
                raise PublishPackageError(
                    f"{label} entry cannot be inspected: {candidate}: {error}"
                ) from error
            relative = candidate.relative_to(resolved).as_posix()
            if stat.S_ISLNK(mode):
                raise PublishPackageError(
                    f"{label} directory contains a symlink: {candidate}"
                )
            if stat.S_ISDIR(mode):
                directories.append(relative)
                visit(candidate)
                continue
            if not stat.S_ISREG(mode):
                raise PublishPackageError(
                    f"{label} directory contains a non-regular file: {candidate}"
                )
            snapshot = _snapshot_file(candidate, f"{label} entry")
            fingerprint = {
                "sha256": snapshot["sha256"],
                "size_bytes": snapshot["size_bytes"],
            }
            total += fingerprint["size_bytes"]
            files.append(
                {
                    "path": relative,
                    "size_bytes": fingerprint["size_bytes"],
                    "sha256": fingerprint["sha256"],
                }
            )

    visit(resolved)
    payload = json.dumps(
        {
            "version": "directory-tree-sha256-v1",
            "directories": sorted(directories),
            "files": sorted(files, key=lambda item: item["path"]),
        },
        ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return {
        "kind": "directory",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "size_bytes": total,
    }


def content_lock_payload_sha256(evidence):
    value = copy.deepcopy(evidence)
    binding = value.get("binding")
    if isinstance(binding, dict):
        binding["payload_sha256"] = None
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def seal_content_lock_evidence(evidence):
    value = copy.deepcopy(evidence)
    if value.get("status") != "sealed":
        raise PublishPackageError("only status=sealed content-lock evidence can be sealed")
    value.setdefault("binding", {})["payload_sha256"] = content_lock_payload_sha256(value)
    errors = validate_document(value, load_schema_json(CONTENT_LOCK_SCHEMA))
    if errors:
        raise PublishPackageError("content-lock evidence is invalid: " + "; ".join(errors))
    return value


def _resolve_lock_artifact(raw_path, *, evidence_path, root, label):
    _validate_clean_path(raw_path, label)
    value = Path(raw_path).expanduser()
    candidate = value if value.is_absolute() else evidence_path.parent / value
    resolved = _artifact_non_symlink(candidate, label)
    if not _inside(resolved, root):
        raise PublishPackageError(f"{label} escapes the platform-master directory: {resolved}")
    return resolved


def validate_content_lock_evidence(
    evidence, evidence_path, manifest_path, master, *, manifest_sha256
):
    errors = validate_document(evidence, load_schema_json(CONTENT_LOCK_SCHEMA))
    if errors:
        raise PublishPackageError("content-lock evidence is invalid: " + "; ".join(errors))
    for field in ("project_id", "video_id"):
        if evidence.get(field) != master[field]:
            raise PublishPackageError(f"content-lock {field} does not match platform master")
    if master["content_lock"]["status"] != "locked":
        if evidence.get("status") != "pending":
            raise PublishPackageError("unlocked master must use pending content-lock evidence")
        return {"status": "pending", "artifacts": {}}
    if evidence.get("status") != "sealed":
        raise PublishPackageError("locked master requires sealed content-lock evidence")
    if evidence.get("platform_master_sha256") != manifest_sha256:
        raise PublishPackageError("content-lock evidence is bound to a different platform master")
    if evidence.get("locked_at") != master["content_lock"]["locked_at"]:
        raise PublishPackageError("content-lock locked_at does not match platform master")
    locked_at = _validate_past_timestamp(evidence.get("locked_at"), "content-lock locked_at")
    created_at = _validate_past_timestamp(evidence.get("created_at"), "content-lock created_at")
    if created_at < locked_at:
        raise PublishPackageError("content-lock created_at cannot precede locked_at")
    approved_at = _validate_past_timestamp(
        master["approval"]["approved_at"], "platform master approved_at"
    )
    if locked_at < approved_at:
        raise PublishPackageError("content-lock locked_at cannot precede master approval")
    if evidence["binding"]["payload_sha256"] != content_lock_payload_sha256(evidence):
        raise PublishPackageError("content-lock evidence payload SHA-256 is invalid")

    artifacts = evidence.get("artifacts")
    roles = [item.get("role") for item in artifacts]
    if set(roles) != CONTENT_LOCK_ROLES or len(roles) != len(CONTENT_LOCK_ROLES):
        raise PublishPackageError(
            "sealed content-lock evidence needs exactly project, cut_plan, and audio_mix"
        )
    root = manifest_path.parent.resolve()
    actual = {}
    resolved_paths = set()
    hash_fields = {
        "project": "project_sha256",
        "cut_plan": "cut_plan_sha256",
        "audio_mix": "audio_mix_sha256",
    }
    for item in artifacts:
        role = item["role"]
        resolved = _resolve_lock_artifact(
            item["path"], evidence_path=evidence_path, root=root,
            label=f"content-lock {role}",
        )
        fingerprint = fingerprint_content_artifact(resolved, f"content-lock {role}")
        if resolved in resolved_paths:
            raise PublishPackageError("content-lock roles must reference distinct artifacts")
        resolved_paths.add(resolved)
        if role in {"cut_plan", "audio_mix"} and fingerprint["kind"] != "file":
            raise PublishPackageError(f"content-lock {role} must be a regular file")
        if item["kind"] != fingerprint["kind"]:
            raise PublishPackageError(f"content-lock {role} kind does not match the artifact")
        for field in ("sha256", "size_bytes"):
            if item[field] != fingerprint[field]:
                raise PublishPackageError(f"content-lock {role} {field} does not match the artifact")
        if master["hashes"][hash_fields[role]] != fingerprint["sha256"]:
            raise PublishPackageError(
                f"platform master {hash_fields[role]} is not the real artifact hash"
            )
        actual[role] = {"path": str(resolved), **fingerprint}

    _validate_clean_path(master["project_path"], "platform master project_path")
    declared_project = Path(master["project_path"]).expanduser()
    project_candidate = declared_project if declared_project.is_absolute() else root / declared_project
    project_path = _artifact_non_symlink(project_candidate, "platform master project_path")
    if project_path != Path(actual["project"]["path"]):
        raise PublishPackageError(
            "platform master project_path differs from the locked project artifact"
        )
    return {"status": "verified", "artifacts": actual}


def _assert_locked_artifacts_unchanged(lock_report):
    """Re-fingerprint every locked artifact immediately before package handoff."""
    if lock_report.get("status") != "verified":
        return
    for role, expected in sorted(lock_report["artifacts"].items()):
        current = fingerprint_content_artifact(
            expected["path"], f"content-lock {role} precommit check"
        )
        for field in ("kind", "sha256", "size_bytes"):
            if current[field] != expected[field]:
                raise PublishPackageError(
                    f"content-lock {role} changed before atomic commit"
                )


def _target_record(target, package_ready, *, catalog_path, catalog_hash, profile, lock_id, lock_hash):
    platform = _safe_fragment(target["platform"], "target platform")
    surface = _safe_fragment(target["surface"], "target surface")
    gates = copy.deepcopy(target["gates"])
    for gate in gates:
        if gate["id"] == "content_lock" and package_ready:
            gate["evidence"] = f"{lock_id} sha256:{lock_hash}"
    downstream = [
        {
            "id": "derivative_render", "status": "pending", "evidence": None,
            "note": "Renderizar el derivado desde el master aprobado sin reabrir el montaje.",
        },
        {
            "id": "technical_delivery_check", "status": "pending", "evidence": None,
            "note": "Validar el archivo derivado con el perfil técnico de la superficie.",
        },
        {
            "id": "human_publication_approval", "status": "pending", "evidence": None,
            "note": "Una persona debe aprobar el derivado exacto antes de publicarlo.",
        },
    ]
    existing = {gate["id"] for gate in gates}
    gates.extend(gate for gate in downstream if gate["id"] not in existing)
    return {
        "profile_id": target["profile_id"],
        "platform": platform,
        "surface": surface,
        "status": "awaiting_derivative_render" if package_ready else "blocked",
        "delivery_output": target["output_path"],
        "brief_output": f"{platform}/{surface}-package-brief.json",
        "provenance": {
            "catalog_path": str(catalog_path),
            "catalog_sha256": catalog_hash,
            "profile_version": profile["profile_version"],
            "evidence_reviewed_at": profile["evidence_reviewed_at"],
        },
        "cover": {
            "status": "draft_required", "aspect_ratio": "9:16",
            "safe_zone_profile": target["profile_id"],
            "creative_direction": (
                "Convertir el hook aprobado en una portada legible en movil; mantener rostro, "
                "promesa y jerarquia dentro de la zona segura del perfil."
            ),
        },
        "copy": {
            "status": "draft_required", "title": None, "caption": None, "cta": None,
            "semantic_guard": (
                "No introducir claims, cifras, promesas o llamados ausentes del master aprobado."
            ),
        },
        "required_gates": [gate["id"] for gate in gates],
        "gates": gates,
    }


def _package_id(video_id, *, source, catalog_sha256, target_profile_ids):
    identity = {
        "video_id": video_id,
        "master_media_sha256": source["sha256"],
        "platform_manifest_sha256": source["platform_manifest_sha256"],
        "approval_receipt_sha256": source["approval_receipt_sha256"],
        "master_profile_report_sha256": source["master_profile_report_sha256"],
        "source_approval_receipt_sha256": source["source_approval_receipt_sha256"],
        "content_lock_evidence_sha256": source["content_lock_evidence_sha256"],
        "catalog_sha256": catalog_sha256,
        "target_profile_ids": sorted(target_profile_ids),
    }
    encoded = json.dumps(
        identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    suffix = hashlib.sha256(encoded).hexdigest()[:16].upper()
    return f"PUBLISH-{_slug(video_id)}-{suffix}"


def _build_brief(package, target):
    brief = {
        "schema_version": "1.0.0",
        "package_id": package["package_id"],
        "video_id": package["video_id"],
        "source_sha256": package["source"]["sha256"],
        "ready_scope": "derivative_build_only",
        "publication_ready": False,
        "target": target,
        "instruction": (
            "Renderizar solo el delta permitido; luego ejecutar el checker tecnico, "
            "validar semantica, revisar la plataforma real y obtener aprobacion humana "
            "del archivo exacto antes de publicar."
        ),
    }
    brief = seal_document(brief)
    errors = validate_document(brief, load_schema_json(BRIEF_SCHEMA))
    if errors:
        raise PublishPackageError("generated package brief is invalid: " + "; ".join(errors))
    return brief


def build_package(
    *, master, master_manifest_path, master_media, receipt, receipt_path,
    source_approval_receipt, source_approval_receipt_path,
    master_profile_report, master_profile_report_path,
    content_lock_evidence, content_lock_evidence_path, catalog,
    catalog_path=DEFAULT_CATALOG, target_ids=None,
    output_dir="publish-package",
):
    """Return a package and delta plan; it never encodes or publishes media."""
    media_snapshot = _snapshot_file(master_media, "master media")
    master_media = media_snapshot["path"]
    manifest_snapshot = _load_bound_json(
        master_manifest_path, master, "platform master manifest"
    )
    manifest_path = manifest_snapshot["path"]
    receipt_snapshot = _load_bound_json(
        receipt_path, receipt, "SDR approval receipt"
    )
    receipt_path = receipt_snapshot["path"]
    source_receipt_snapshot = _load_bound_json(
        source_approval_receipt_path, source_approval_receipt,
        "editorial approval receipt",
    )
    source_receipt_path = source_receipt_snapshot["path"]
    report_snapshot = _load_bound_json(
        master_profile_report_path, master_profile_report, "master profile report"
    )
    report_path = report_snapshot["path"]
    lock_snapshot = _load_bound_json(
        content_lock_evidence_path, content_lock_evidence, "content-lock evidence"
    )
    lock_path = lock_snapshot["path"]
    catalog_snapshot = _load_bound_json(
        catalog_path, catalog, "platform catalog"
    )
    catalog_path = catalog_snapshot["path"]
    try:
        validate_catalog_document(catalog)
        validate_master(master, catalog)
    except (PlatformPlanError, KeyError, TypeError, ValueError) as error:
        raise PublishPackageError(f"invalid platform master: {error}") from error

    receipt_report = validate_source_receipt(receipt, receipt_path, master_media, master)
    if (
        media_snapshot["sha256"] != receipt_report["actual_artifact_sha256"]
        or media_snapshot["size_bytes"] != receipt_report["actual_size_bytes"]
    ):
        raise PublishPackageError("SDR master changed during approval verification")
    source_candidate = resolve_artifact_path(
        source_approval_receipt, receipt_path=source_receipt_path
    )
    if source_candidate is None:
        raise PublishPackageError("editorial approval receipt has no artifact path")
    source_media_snapshot = _snapshot_file(source_candidate, "approved editorial source")
    replay, source_media, source_receipt_report = validate_master_profile_report(
        master_profile_report, receipt_report["actual_artifact_sha256"], master,
        master_media=master_media, report_path=report_path,
        source_receipt=source_approval_receipt,
        source_receipt_path=source_receipt_path,
    )
    if source_media_snapshot["path"] != source_media or (
        source_media_snapshot["sha256"] != source_receipt_report["actual_artifact_sha256"]
    ):
        raise PublishPackageError("editorial source changed during profile validation")
    _assert_snapshot_unchanged(source_media_snapshot, "approved editorial source")
    lock_report = validate_content_lock_evidence(
        content_lock_evidence,
        lock_path,
        manifest_path,
        master,
        manifest_sha256=manifest_snapshot["sha256"],
    )
    try:
        adaptation = build_plan(
            master, catalog, target_ids=target_ids, master_path=manifest_path,
            catalog_path=catalog_path, output_dir=output_dir,
        )
    except (PlatformPlanError, KeyError, TypeError, ValueError) as error:
        raise PublishPackageError(str(error)) from error

    package_ready = (
        adaptation["status"] == "ready_for_platform_preview"
        and lock_report["status"] == "verified"
        and replay["publication_ready"] is True
    )
    blockers = list(adaptation["blocking_reasons"])
    if lock_report["status"] != "verified":
        blockers.append("La evidencia del bloqueo de contenido no está verificada.")
    catalog_hash = catalog_snapshot["sha256"]
    lock_hash = lock_snapshot["sha256"]
    profile_by_id = {profile["id"]: profile for profile in catalog["profiles"]}
    source_record = {
        "path": str(master_media),
        "sha256": media_snapshot["sha256"],
        "size_bytes": media_snapshot["size_bytes"],
        "media_role": SOCIAL_ROLE,
        "master_profile_id": SOCIAL_PROFILE,
        "platform_manifest_path": str(manifest_path),
        "platform_manifest_sha256": manifest_snapshot["sha256"],
        "approval_receipt_path": str(receipt_path),
        "approval_receipt_sha256": receipt_snapshot["sha256"],
        "approval_receipt_id": receipt["receipt_id"],
        "master_profile_report_path": str(report_path),
        "master_profile_report_sha256": report_snapshot["sha256"],
        "source_media_path": str(source_media),
        "source_media_sha256": source_media_snapshot["sha256"],
        "source_approval_receipt_path": str(source_receipt_path),
        "source_approval_receipt_sha256": source_receipt_snapshot["sha256"],
        "source_approval_receipt_id": source_approval_receipt["receipt_id"],
        "content_lock_evidence_path": str(lock_path),
        "content_lock_evidence_sha256": lock_hash,
        "content_lock_id": content_lock_evidence["lock_id"],
    }
    target_records = [
        _target_record(
            item, package_ready, catalog_path=catalog_path,
            catalog_hash=catalog_hash, profile=profile_by_id[item["profile_id"]],
            lock_id=content_lock_evidence["lock_id"], lock_hash=lock_hash,
        )
        for item in adaptation["targets"]
    ]
    package = {
        "schema_version": "1.2.0",
        "package_id": _package_id(
            master["video_id"], source=source_record,
            catalog_sha256=catalog_hash,
            target_profile_ids=[item["profile_id"] for item in adaptation["targets"]],
        ),
        "project_id": master["project_id"],
        "video_id": master["video_id"],
        "generated_at": adaptation["generated_at"],
        "status": "ready_for_derivative_build" if package_ready else "blocked",
        "blocking_reasons": blockers,
        "source": source_record,
        "adaptation": {
            "status": adaptation["status"],
            "strategy": adaptation["policy"]["strategy"],
            "catalog_version": adaptation["catalog"]["catalog_version"],
            "catalog_path": str(catalog_path),
            "catalog_sha256": catalog_hash,
            "target_count": len(adaptation["targets"]),
            "plan_output": "platform-adaptation.json",
        },
        "targets": target_records,
        "governance": {
            "auto_publish": False,
            "reedit_master": False,
            "derivative_must_preserve_semantics": True,
            "live_platform_preview_required": True,
            "human_publication_approval_required": True,
            "cryptographic_identity_established": False,
            "ready_scope": "derivative_build_only",
            "publication_ready": False,
            "integrity_notice": (
                "SHA-256 and sealed payloads verify file integrity and declared lineage, not the "
                "cryptographic identity of a human approver. This package only authorizes "
                "building derivatives; it never authorizes publication."
            ),
        },
    }
    brief_paths = [target["brief_output"] for target in package["targets"]]
    if len(brief_paths) != len(set(brief_paths)):
        raise PublishPackageError("target brief paths are not unique")
    briefs = [_build_brief(package, target) for target in package["targets"]]
    package["bundle"] = {
        "adaptation_payload_sha256": adaptation["binding"]["payload_sha256"],
        "briefs": [
            {
                "path": target["brief_output"],
                "payload_sha256": brief["binding"]["payload_sha256"],
            }
            for target, brief in zip(package["targets"], briefs)
        ],
    }
    package = seal_document(package)
    errors = validate_document(package, load_schema_json(PACKAGE_SCHEMA))
    if errors:
        raise PublishPackageError("generated package is invalid: " + "; ".join(errors))
    adaptation_errors = validate_document(adaptation, load_schema_json(ADAPTATION_SCHEMA))
    if adaptation_errors:
        raise PublishPackageError(
            "generated adaptation is invalid: " + "; ".join(adaptation_errors)
        )
    try:
        verify_document_binding(package, "publish package")
        verify_document_binding(adaptation, "platform adaptation")
    except PlatformPlanError as error:
        raise PublishPackageError(str(error)) from error
    for snapshot, label in (
        (media_snapshot, "master media"),
        (source_media_snapshot, "approved editorial source"),
        (manifest_snapshot, "platform master manifest"),
        (receipt_snapshot, "SDR approval receipt"),
        (source_receipt_snapshot, "editorial approval receipt"),
        (report_snapshot, "master profile report"),
        (lock_snapshot, "content-lock evidence"),
        (catalog_snapshot, "platform catalog"),
    ):
        _assert_snapshot_unchanged(snapshot, label)
    _assert_locked_artifacts_unchanged(lock_report)
    return package, adaptation


def _validate_declared_paths(package, adaptation):
    source = package["source"]
    for key in (
        "path", "platform_manifest_path", "approval_receipt_path",
        "master_profile_report_path", "source_media_path",
        "source_approval_receipt_path", "content_lock_evidence_path",
    ):
        _validate_clean_path(source[key], f"package source.{key}")
    _validate_clean_path(adaptation["master"]["manifest_path"], "adaptation master path")
    _validate_clean_path(adaptation["catalog"]["path"], "adaptation catalog path")
    _validate_clean_path(adaptation["output_root"], "adaptation output root")
    _validate_clean_path(package["adaptation"]["catalog_path"], "package catalog path")
    _validate_clean_path(
        package["adaptation"]["plan_output"], "adaptation plan output", relative=True
    )
    for index, target in enumerate(package["targets"]):
        _validate_clean_path(target["delivery_output"], f"target {index} delivery output")
        _validate_clean_path(
            target["brief_output"], f"target {index} brief output", relative=True
        )
        _validate_clean_path(
            target["provenance"]["catalog_path"], f"target {index} catalog path"
        )
    for index, target in enumerate(adaptation["targets"]):
        _validate_clean_path(target["output_path"], f"adaptation target {index} output")
    for index, item in enumerate(package["bundle"]["briefs"]):
        _validate_clean_path(item["path"], f"bundle brief {index} path", relative=True)


def _require_snapshot_hash(snapshot, expected, label):
    if snapshot["sha256"] != expected:
        raise PublishPackageError(f"{label} SHA-256 differs from the sealed package")


def validate_materialization_contract(package, adaptation):
    """Revalidate a sealed package, its plan, and all live provenance inputs."""
    package_errors = validate_document(package, load_schema_json(PACKAGE_SCHEMA))
    if package_errors:
        raise PublishPackageError("publish package is invalid: " + "; ".join(package_errors))
    adaptation_errors = validate_document(adaptation, load_schema_json(ADAPTATION_SCHEMA))
    if adaptation_errors:
        raise PublishPackageError(
            "platform adaptation is invalid: " + "; ".join(adaptation_errors)
        )
    try:
        verify_document_binding(package, "publish package")
        verify_document_binding(adaptation, "platform adaptation")
    except PlatformPlanError as error:
        raise PublishPackageError(str(error)) from error
    _validate_declared_paths(package, adaptation)
    if package["status"] != "ready_for_derivative_build" or package["blocking_reasons"]:
        raise PublishPackageError("only a blocker-free derivative-build package may be materialized")
    governance = package["governance"]
    if (
        governance["ready_scope"] != "derivative_build_only"
        or governance["publication_ready"] is not False
        or governance["auto_publish"] is not False
        or governance["cryptographic_identity_established"] is not False
    ):
        raise PublishPackageError("package governance overstates publication authority")

    source = package["source"]
    manifest_snapshot = _snapshot_json(source["platform_manifest_path"], "platform master manifest")
    receipt_snapshot = _snapshot_json(source["approval_receipt_path"], "SDR approval receipt")
    report_snapshot = _snapshot_json(source["master_profile_report_path"], "master profile report")
    source_receipt_snapshot = _snapshot_json(
        source["source_approval_receipt_path"], "editorial approval receipt"
    )
    lock_snapshot = _snapshot_json(source["content_lock_evidence_path"], "content-lock evidence")
    catalog_snapshot = _snapshot_json(package["adaptation"]["catalog_path"], "platform catalog")
    media_snapshot = _snapshot_file(source["path"], "SDR master")
    source_media_snapshot = _snapshot_file(source["source_media_path"], "editorial source")
    snapshot_expectations = (
        (manifest_snapshot, source["platform_manifest_sha256"], "platform master manifest"),
        (receipt_snapshot, source["approval_receipt_sha256"], "SDR approval receipt"),
        (report_snapshot, source["master_profile_report_sha256"], "master profile report"),
        (
            source_receipt_snapshot,
            source["source_approval_receipt_sha256"],
            "editorial approval receipt",
        ),
        (lock_snapshot, source["content_lock_evidence_sha256"], "content-lock evidence"),
        (catalog_snapshot, package["adaptation"]["catalog_sha256"], "platform catalog"),
        (media_snapshot, source["sha256"], "SDR master"),
        (source_media_snapshot, source["source_media_sha256"], "editorial source"),
    )
    for snapshot, expected_hash, label in snapshot_expectations:
        _require_snapshot_hash(snapshot, expected_hash, label)
    if media_snapshot["size_bytes"] != source["size_bytes"]:
        raise PublishPackageError("SDR master size differs from the sealed package")

    master = manifest_snapshot["document"]
    receipt = receipt_snapshot["document"]
    report = report_snapshot["document"]
    source_receipt = source_receipt_snapshot["document"]
    lock = lock_snapshot["document"]
    catalog = catalog_snapshot["document"]
    try:
        validate_catalog_document(catalog)
        validate_master(master, catalog)
    except (PlatformPlanError, KeyError, TypeError, ValueError) as error:
        raise PublishPackageError(f"invalid materialization provenance: {error}") from error
    if package["project_id"] != master["project_id"] or package["video_id"] != master["video_id"]:
        raise PublishPackageError("package project/video does not match platform master")
    if receipt.get("receipt_id") != source["approval_receipt_id"]:
        raise PublishPackageError("SDR approval receipt id differs from package provenance")
    if source_receipt.get("receipt_id") != source["source_approval_receipt_id"]:
        raise PublishPackageError("editorial receipt id differs from package provenance")
    if lock.get("lock_id") != source["content_lock_id"]:
        raise PublishPackageError("content-lock id differs from package provenance")

    receipt_report = validate_source_receipt(
        receipt, receipt_snapshot["path"], media_snapshot["path"], master
    )
    replay, resolved_source_media, source_receipt_report = validate_master_profile_report(
        report,
        receipt_report["actual_artifact_sha256"],
        master,
        master_media=media_snapshot["path"],
        report_path=report_snapshot["path"],
        source_receipt=source_receipt,
        source_receipt_path=source_receipt_snapshot["path"],
    )
    if resolved_source_media != source_media_snapshot["path"]:
        raise PublishPackageError("resolved editorial source differs from package provenance")
    if source_receipt_report["actual_artifact_sha256"] != source["source_media_sha256"]:
        raise PublishPackageError("editorial source hash differs from package provenance")
    if replay["publication_ready"] is not True:
        raise PublishPackageError("SDR profile replay is not ready for derivative construction")
    lock_report = validate_content_lock_evidence(
        lock,
        lock_snapshot["path"],
        manifest_snapshot["path"],
        master,
        manifest_sha256=manifest_snapshot["sha256"],
    )
    if lock_report["status"] != "verified":
        raise PublishPackageError("content-lock evidence is not verified")

    target_ids = [target["profile_id"] for target in package["targets"]]
    expected_adaptation = build_plan(
        master,
        catalog,
        target_ids=target_ids,
        master_path=manifest_snapshot["path"],
        catalog_path=catalog_snapshot["path"],
        output_dir=adaptation["output_root"],
    )
    expected_adaptation["generated_at"] = adaptation["generated_at"]
    expected_adaptation = seal_document(expected_adaptation)
    if expected_adaptation != adaptation:
        raise PublishPackageError("platform adaptation differs from the current catalog/master contract")
    if package["generated_at"] != adaptation["generated_at"]:
        raise PublishPackageError("package and adaptation generated_at values differ")
    expected_adaptation_summary = {
        "status": adaptation["status"],
        "strategy": adaptation["policy"]["strategy"],
        "catalog_version": adaptation["catalog"]["catalog_version"],
        "catalog_path": str(catalog_snapshot["path"]),
        "catalog_sha256": catalog_snapshot["sha256"],
        "target_count": len(adaptation["targets"]),
        "plan_output": "platform-adaptation.json",
    }
    if package["adaptation"] != expected_adaptation_summary:
        raise PublishPackageError("package adaptation summary is inconsistent")

    profile_by_id = {profile["id"]: profile for profile in catalog["profiles"]}
    expected_targets = [
        _target_record(
            target,
            True,
            catalog_path=catalog_snapshot["path"],
            catalog_hash=catalog_snapshot["sha256"],
            profile=profile_by_id[target["profile_id"]],
            lock_id=lock["lock_id"],
            lock_hash=lock_snapshot["sha256"],
        )
        for target in adaptation["targets"]
    ]
    if package["targets"] != expected_targets:
        raise PublishPackageError("package targets, gates, states, or provenance are inconsistent")
    for target in package["targets"]:
        gates = {gate["id"]: gate for gate in target["gates"]}
        human_gate = gates.get("human_publication_approval")
        if not human_gate or human_gate["status"] != "pending" or human_gate["evidence"] is not None:
            raise PublishPackageError("human publication approval must remain pending")

    expected_id = _package_id(
        package["video_id"],
        source=source,
        catalog_sha256=catalog_snapshot["sha256"],
        target_profile_ids=target_ids,
    )
    if package["package_id"] != expected_id:
        raise PublishPackageError("package_id is not bound to catalog, targets, lock, and report")
    briefs = [_build_brief(package, target) for target in package["targets"]]
    expected_bundle = {
        "adaptation_payload_sha256": adaptation["binding"]["payload_sha256"],
        "briefs": [
            {"path": target["brief_output"], "payload_sha256": brief["binding"]["payload_sha256"]}
            for target, brief in zip(package["targets"], briefs)
        ],
    }
    if package["bundle"] != expected_bundle:
        raise PublishPackageError("package bundle seal does not match adaptation and briefs")
    snapshots = [item[0] for item in snapshot_expectations]
    return briefs, snapshots, lock_report


def _assert_safe_output_dir(path):
    _validate_clean_path(path, "output path")
    raw = _assert_no_symlink_chain(path, "output path")
    resolved = raw.resolve(strict=False)
    if resolved.exists() and not resolved.is_dir():
        raise PublishPackageError(f"output path is not a directory: {resolved}")
    return resolved


def _assert_destination_parent(out_dir, destination):
    try:
        relative = destination.relative_to(out_dir)
    except ValueError as error:
        raise PublishPackageError(
            f"package destination escapes output directory: {destination}"
        ) from error
    cursor = out_dir
    for part in relative.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise PublishPackageError(f"package destination traverses a symlink: {cursor}")


def _write_staged_document(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    encoded = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as error:
        raise PublishPackageError(f"cannot create staged package file {path}: {error}") from error
    try:
        offset = 0
        while offset < len(encoded):
            written = os.write(descriptor, encoded[offset:])
            if written <= 0:
                raise PublishPackageError(f"short write while staging {path}")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _fsync_directory(path):
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_CLOEXEC", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _assert_tree_has_no_symlinks(root, label):
    try:
        entries = list(os.scandir(root))
    except OSError as error:
        raise PublishPackageError(f"{label} cannot be read safely: {error}") from error
    for entry in entries:
        try:
            mode = entry.stat(follow_symlinks=False).st_mode
        except OSError as error:
            raise PublishPackageError(f"{label} entry cannot be inspected: {entry.path}") from error
        if stat.S_ISLNK(mode):
            raise PublishPackageError(f"{label} contains a symlink: {entry.path}")
        if stat.S_ISDIR(mode):
            _assert_tree_has_no_symlinks(Path(entry.path), label)
        elif not stat.S_ISREG(mode):
            raise PublishPackageError(f"{label} contains a non-regular entry: {entry.path}")


def _assert_existing_package_directory(out_dir):
    """Refuse --force unless the destination is a valid package made by this tool."""
    checks = (
        ("publish-package.json", PACKAGE_SCHEMA, "existing publish package"),
        ("platform-adaptation.json", ADAPTATION_SCHEMA, "existing platform adaptation"),
    )
    for name, schema_path, label in checks:
        snapshot = _snapshot_json(out_dir / name, label)
        errors = validate_document(snapshot["document"], load_schema_json(schema_path))
        if errors:
            raise PublishPackageError(
                f"refusing to replace an invalid {label}: " + "; ".join(errors)
            )
        try:
            verify_document_binding(snapshot["document"], label)
        except PlatformPlanError as error:
            raise PublishPackageError(
                f"refusing to replace an unsealed {label}: {error}"
            ) from error


def _assert_output_separate_from_inputs(out_dir, snapshots, lock_report):
    for snapshot in snapshots:
        protected = snapshot["path"]
        if protected == out_dir or _inside(protected, out_dir):
            raise PublishPackageError(
                f"output directory may not contain provenance input: {protected}"
            )
    for role, artifact in lock_report.get("artifacts", {}).items():
        protected = Path(artifact["path"])
        if (
            protected == out_dir
            or _inside(protected, out_dir)
            or (artifact["kind"] == "directory" and _inside(out_dir, protected))
        ):
            raise PublishPackageError(
                f"output directory overlaps content-lock {role}: {protected}"
            )


def materialize(package, adaptation, out_dir, *, force=False):
    briefs, provenance_snapshots, lock_report = validate_materialization_contract(
        package, adaptation
    )
    out_dir = _assert_safe_output_dir(out_dir)
    _assert_output_separate_from_inputs(out_dir, provenance_snapshots, lock_report)
    parent = out_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    _assert_no_symlink_chain(parent, "output parent")
    if out_dir.exists() or out_dir.is_symlink():
        if out_dir.is_symlink():
            raise PublishPackageError(f"output path cannot be a symlink: {out_dir}")
        if not out_dir.is_dir():
            raise PublishPackageError(f"output path is not a directory: {out_dir}")
        _assert_tree_has_no_symlinks(out_dir, "existing package directory")
        if not force:
            raise PublishPackageError(
                f"refusing to replace an existing package directory without --force: {out_dir}"
            )
        _assert_existing_package_directory(out_dir)

    documents = {
        "publish-package.json": package,
        "platform-adaptation.json": adaptation,
    }
    for target, brief in zip(package["targets"], briefs):
        documents[target["brief_output"]] = brief
    if len(documents) != 2 + len(package["targets"]):
        raise PublishPackageError("package contains duplicate output destinations")

    staging = Path(tempfile.mkdtemp(prefix=f".{out_dir.name}.stage-", dir=parent))
    backup = None
    committed = False
    try:
        for relative_text, document in documents.items():
            _validate_clean_path(relative_text, "package destination", relative=True)
            destination = staging / relative_text
            _assert_destination_parent(staging, destination)
            _write_staged_document(destination, document)
        for path in sorted(
            {staging, *(item.parent for item in staging.rglob("*"))},
            key=lambda item: len(item.parts),
            reverse=True,
        ):
            if path.is_dir():
                _fsync_directory(path)
        for relative_text, document in documents.items():
            staged = _snapshot_json(staging / relative_text, f"staged {relative_text}")
            if staged["document"] != document:
                raise PublishPackageError(f"staged document changed: {relative_text}")
        for snapshot in provenance_snapshots:
            _assert_snapshot_unchanged(snapshot, f"provenance {snapshot['path'].name}")
        _assert_locked_artifacts_unchanged(lock_report)

        if out_dir.exists():
            backup = Path(tempfile.mkdtemp(prefix=f".{out_dir.name}.backup-", dir=parent))
            backup.rmdir()
            os.replace(out_dir, backup)
        try:
            os.replace(staging, out_dir)
            committed = True
            _fsync_directory(parent)
        except Exception:
            if backup is not None and backup.exists() and not out_dir.exists():
                os.replace(backup, out_dir)
            raise
        if backup is not None and backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if not committed and staging.exists():
            shutil.rmtree(staging)
        raise
    return out_dir


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master-manifest", type=Path, required=True)
    parser.add_argument("--master-media", type=Path, required=True)
    parser.add_argument("--approval-receipt", type=Path, required=True)
    parser.add_argument("--source-approval-receipt", type=Path, required=True)
    parser.add_argument("--master-profile-report", type=Path, required=True)
    parser.add_argument("--content-lock-evidence", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--target", action="append")
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--write", action="store_true", help="materialize files; dry-run otherwise")
    parser.add_argument("--force", action="store_true", help="replace an existing package; requires --write")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        master = read_json(args.master_manifest, "platform master")
        receipt = load_receipt_json(args.approval_receipt, "approval receipt")
        source_receipt = load_receipt_json(
            args.source_approval_receipt, "source approval receipt"
        )
        master_profile_report = read_json(
            args.master_profile_report, "master profile report"
        )
        content_lock_evidence = read_json(
            args.content_lock_evidence, "content-lock evidence"
        )
        catalog = load_catalog(args.catalog)
        package, adaptation = build_package(
            master=master,
            master_manifest_path=args.master_manifest,
            master_media=args.master_media,
            receipt=receipt,
            receipt_path=args.approval_receipt,
            source_approval_receipt=source_receipt,
            source_approval_receipt_path=args.source_approval_receipt,
            master_profile_report=master_profile_report,
            master_profile_report_path=args.master_profile_report,
            content_lock_evidence=content_lock_evidence,
            content_lock_evidence_path=args.content_lock_evidence,
            catalog=catalog,
            catalog_path=args.catalog,
            target_ids=_parse_targets(args.target),
            output_dir=args.out_dir,
        )
        if args.force and not args.write:
            raise PublishPackageError("--force requires --write")
        if args.write:
            materialize(package, adaptation, args.out_dir, force=args.force)
        print(json.dumps(package, ensure_ascii=False, indent=2))
        if package["status"] == "blocked":
            print("BLOCKED: publication package is not ready", file=sys.stderr)
            return 3
        return 0
    except (
        ApprovalReceiptError, MasterProfileError, PublishPackageError,
        PlatformPlanError, json.JSONDecodeError, KeyError, OSError,
        TypeError, ValueError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
