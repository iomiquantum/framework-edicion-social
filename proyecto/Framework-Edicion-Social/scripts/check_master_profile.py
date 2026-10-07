#!/usr/bin/env python3
"""Read-only checker for trusted editorial HDR and social SDR profiles.

The checker validates encoded media, hash-bound loudness/probe evidence, and
the approved-source lineage required by a social delivery master. SDR delivery
also requires a declared tone-map record and a human visual review bound to the
output hash. Hashes establish integrity and declared lineage, not identity or
non-repudiation. The checker never transcodes media and only writes a report
when both ``--out`` and ``--write`` are supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
FRAMEWORK_ROOT = SCRIPT_DIR.parent
DEFAULT_SCHEMA = FRAMEWORK_ROOT / "schemas/master-profile.schema.json"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from approval_receipt import (  # noqa: E402
    ApprovalReceiptError,
    atomic_write_text,
    file_fingerprint,
    is_human_identity,
    is_verifiable_human_reference,
    load_json,
    parse_rfc3339,
    resolve_artifact_path,
    verify_receipt,
)
from check_platform_delivery import (  # noqa: E402
    DeliveryCheckError,
    parse_ffprobe,
    run_ffprobe,
    utc_now,
)
from schema_validation import UnsupportedSchemaKeyword, validate_document  # noqa: E402


class MasterProfileError(ValueError):
    """Master profile, measurement, or lineage evidence is malformed."""


SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
TRUSTED_PROFILE_REGISTRY = {
    "MASTER-PROFILE-EDITORIAL-HDR-001": {
        "relative_path": "master-profiles/editorial-mezzanine-hdr-001.json",
        "profile_version": "1.0.0",
        "file_sha256": "4a69faaac32f429615d97863d1b84f70940103c8c3cdec60ecb72f70e7615a1c",
        "canonical_sha256": "a7185bbf8b484d9d9658e8b37d75ca4804187aaac3fa94085cfb7bf7741d369a",
    },
    "MASTER-PROFILE-SOCIAL-SDR-001": {
        "relative_path": "master-profiles/social-delivery-sdr-001.json",
        "profile_version": "1.0.0",
        "file_sha256": "8e430a8a4fd4c92ff1814afc6579691c476707f193d663cebb3f0fef8acceeaf",
        "canonical_sha256": "62d110b2041f070798b2c1e410adae0520d22c0ddd328def36a478f13c5e2afb",
    },
}
TONE_MAP_REQUIRED_FIELDS = {
    "schema_version",
    "kind",
    "project_id",
    "video_id",
    "source_sha256",
    "output_sha256",
    "source_profile_id",
    "output_profile_id",
    "tool",
    "tool_version",
    "method",
    "parameters",
    "performed_at",
}
VISUAL_REVIEW_CHECKS = {
    "skin_tones_natural",
    "highlights_not_clipped",
    "shadows_not_crushed",
    "gradients_clean",
    "captions_legible",
    "face_unobscured",
    "audio_video_in_sync",
}
VISUAL_REVIEW_REQUIRED_FIELDS = {
    "schema_version",
    "kind",
    "project_id",
    "video_id",
    "output_sha256",
    "profile_id",
    "reviewer",
    "reviewed_at",
    "reference",
    "checks",
    "note",
}


def _semantic_profile_errors(profile):
    errors = []
    video = profile.get("video", {})
    audio = profile.get("audio", {})
    governance = profile.get("governance", {})
    if video.get("duration_max_seconds", 0) < video.get("duration_min_seconds", 0):
        errors.append("duration_max_seconds is below duration_min_seconds")
    minimum = video.get("bitrate_min_mbps")
    maximum = video.get("bitrate_max_mbps")
    if minimum is not None and maximum is not None and maximum < minimum:
        errors.append("bitrate_max_mbps is below bitrate_min_mbps")
    if audio.get("requires_loudness_scan") and any(
        audio.get(field) is None for field in ("target_lufs", "lufs_tolerance", "true_peak_max_dbtp")
    ):
        errors.append("a required loudness scan needs target, tolerance, and true-peak limit")

    role = profile.get("artifact_role")
    if role == "editorial_mezzanine":
        if profile.get("color_intent") != "preserve_hdr":
            errors.append("editorial mezzanine must preserve HDR")
        if not governance.get("editable_source") or governance.get("upload_ready"):
            errors.append("editorial mezzanine must be editable and not upload-ready")
        if governance.get("requires_approved_source_receipt"):
            errors.append("editorial mezzanine cannot require an approved parent")
        if governance.get("required_source_media_role") is not None:
            errors.append("editorial mezzanine cannot declare a required source role")
        if governance.get("required_source_profile_id") is not None:
            errors.append("editorial mezzanine cannot declare a required source profile")
        if governance.get("source_hash_must_differ"):
            errors.append("editorial mezzanine cannot require a distinct parent hash")
        if not set(video.get("color_primaries", [])).issubset({"bt2020"}):
            errors.append("editorial mezzanine color primaries must remain BT.2020")
        if not set(video.get("color_transfers", [])).issubset({"arib-std-b67", "smpte2084"}):
            errors.append("editorial mezzanine transfers must be HLG or PQ")
        if not set(video.get("color_spaces", [])).issubset({"bt2020nc", "bt2020ncl"}):
            errors.append("editorial mezzanine color space must remain BT.2020 non-constant luminance")
    elif role == "social_delivery_master":
        if profile.get("color_intent") != "normalize_sdr_bt709":
            errors.append("social delivery master must normalize to SDR BT.709")
        if governance.get("editable_source") or not governance.get("upload_ready"):
            errors.append("social delivery master must be upload-oriented and not the editing source")
        if not governance.get("requires_approved_source_receipt"):
            errors.append("social delivery master must require an approved source receipt")
        if governance.get("required_source_media_role") != "editorial_mezzanine":
            errors.append("social delivery master must require an editorial mezzanine source")
        if governance.get("required_source_profile_id") != "MASTER-PROFILE-EDITORIAL-HDR-001":
            errors.append("social delivery master must require the trusted editorial HDR profile")
        if not governance.get("source_hash_must_differ"):
            errors.append("social delivery master must require a distinct derived hash")
        if set(video.get("color_primaries", [])) != {"bt709"}:
            errors.append("social delivery master color primaries must be BT.709")
        if set(video.get("color_transfers", [])) != {"bt709"}:
            errors.append("social delivery master transfer must be BT.709")
        if set(video.get("color_spaces", [])) != {"bt709"}:
            errors.append("social delivery master color space must be BT.709")
    return errors


def canonical_profile_sha256(profile):
    encoded = json.dumps(profile, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _trusted_profile_entry(profile):
    entry = TRUSTED_PROFILE_REGISTRY.get(profile.get("id"))
    if entry is None:
        raise MasterProfileError(f"untrusted master profile id: {profile.get('id')!r}")
    if profile.get("status") != "active":
        raise MasterProfileError(f"trusted master profile must be active, got {profile.get('status')!r}")
    if profile.get("profile_version") != entry["profile_version"]:
        raise MasterProfileError("master profile version does not match the trusted registry")
    actual_canonical = canonical_profile_sha256(profile)
    if actual_canonical != entry["canonical_sha256"]:
        raise MasterProfileError("master profile contents do not match the trusted canonical hash")
    return entry


def load_profile(profile_path, schema_path=DEFAULT_SCHEMA, *, require_trusted=True):
    profile = load_json(profile_path, "master profile")
    schema = load_json(schema_path, "master profile schema")
    try:
        errors = validate_document(profile, schema)
    except UnsupportedSchemaKeyword as error:
        raise MasterProfileError(f"unsupported master profile schema: {error}") from error
    if not errors:
        errors.extend(_semantic_profile_errors(profile))
    if errors:
        raise MasterProfileError("invalid master profile: " + "; ".join(errors))
    if require_trusted:
        entry = _trusted_profile_entry(profile)
        expected_path = (FRAMEWORK_ROOT / entry["relative_path"]).resolve()
        actual_path = Path(profile_path).expanduser().resolve()
        if actual_path != expected_path:
            raise MasterProfileError(f"trusted profile must be loaded from {expected_path}")
        fingerprint = file_fingerprint(actual_path)
        if fingerprint["sha256"] != entry["file_sha256"]:
            raise MasterProfileError("master profile file hash does not match the trusted registry")
    return profile


def _finding(severity, code, message):
    return {"severity": severity, "code": code, "message": message}


def _normalized(value):
    return str(value).strip().lower()


def _allowed(findings, actual, allowed, code, label, severity="error"):
    expected = {_normalized(value) for value in allowed}
    if _normalized(actual) not in expected:
        findings.append(
            _finding(severity, code, f"{label}: got {actual!r}, expected one of {sorted(expected)!r}")
        )


def _equal(findings, actual, expected, code, label, severity="error", tolerance=None):
    if tolerance is None:
        matched = _normalized(actual) == _normalized(expected)
    else:
        matched = actual is not None and abs(float(actual) - float(expected)) <= tolerance
    if not matched:
        findings.append(_finding(severity, code, f"{label}: got {actual!r}, expected {expected!r}"))


def pixel_bit_depth(pixel_format):
    value = _normalized(pixel_format)
    match = re.search(r"p0?(10|12|16)(?:le|be)?$", value)
    if match:
        return int(match.group(1))
    if value in {"yuv420p", "yuv422p", "yuv444p", "nv12", "rgb24", "bgr24"}:
        return 8
    return None


def parse_loudness(document):
    if not isinstance(document, dict):
        raise MasterProfileError("loudness result must be a JSON object")
    integrated = document.get("integrated_lufs", document.get("input_i"))
    true_peak = document.get("true_peak_dbtp", document.get("input_tp"))
    try:
        integrated = float(integrated)
        true_peak = float(true_peak)
    except (TypeError, ValueError) as error:
        raise MasterProfileError("loudness result requires numeric integrated_lufs/input_i and true_peak_dbtp/input_tp") from error
    if not math.isfinite(integrated) or not math.isfinite(true_peak):
        raise MasterProfileError("loudness values must be finite numbers")
    return {"integrated_lufs": integrated, "true_peak_dbtp": true_peak}


def _validate_evidence_timestamp(value, label):
    parsed = parse_rfc3339(value)
    if parsed is None:
        raise MasterProfileError(f"{label} must be an RFC 3339 timestamp")
    if parsed > datetime.now(timezone.utc):
        raise MasterProfileError(f"{label} cannot be in the future")
    return parsed


def _exact_fields(document, expected, label):
    if not isinstance(document, dict) or set(document) != expected:
        raise MasterProfileError(f"{label} fields must be exactly {sorted(expected)}")


def load_probe_evidence(path, expected_media_sha256, label="probe evidence"):
    document = load_json(path, label)
    expected = {
        "schema_version",
        "kind",
        "authoritative",
        "media_sha256",
        "captured_at",
        "tool",
        "probe",
    }
    _exact_fields(document, expected, label)
    if document["schema_version"] != "1.0.0":
        raise MasterProfileError(f"{label} has unsupported schema_version")
    authoritative = document["authoritative"]
    if not isinstance(authoritative, bool):
        raise MasterProfileError(f"{label} authoritative must be boolean")
    if authoritative:
        if document["kind"] != "ffprobe_capture":
            raise MasterProfileError(f"{label} authoritative evidence must use kind=ffprobe_capture")
        if document["media_sha256"] != expected_media_sha256:
            raise MasterProfileError(f"{label} media_sha256 does not match the inspected media")
        _validate_evidence_timestamp(document["captured_at"], f"{label} captured_at")
        if not isinstance(document["tool"], str) or not document["tool"].strip():
            raise MasterProfileError(f"{label} tool must be non-empty")
    else:
        if document["kind"] != "ffprobe_fixture":
            raise MasterProfileError(f"{label} non-authoritative evidence must use kind=ffprobe_fixture")
        if document["media_sha256"] is not None or document["captured_at"] is not None:
            raise MasterProfileError(f"{label} fixture cannot claim a media binding or capture time")
    if not isinstance(document["probe"], dict):
        raise MasterProfileError(f"{label} probe must be an object")
    return document["probe"], authoritative, {
        key: document[key] for key in expected - {"probe"}
    }


def load_loudness_evidence(path, expected_media_sha256):
    document = load_json(path, "loudness evidence")
    expected = {
        "schema_version",
        "kind",
        "authoritative",
        "media_sha256",
        "measured_at",
        "tool",
        "measurement",
    }
    _exact_fields(document, expected, "loudness evidence")
    if document["schema_version"] != "1.0.0":
        raise MasterProfileError("loudness evidence has unsupported schema_version")
    authoritative = document["authoritative"]
    if not isinstance(authoritative, bool):
        raise MasterProfileError("loudness evidence authoritative must be boolean")
    if authoritative:
        if document["kind"] != "loudness_measurement":
            raise MasterProfileError("authoritative loudness evidence must use kind=loudness_measurement")
        if document["media_sha256"] != expected_media_sha256:
            raise MasterProfileError("loudness evidence media_sha256 does not match the inspected media")
        _validate_evidence_timestamp(document["measured_at"], "loudness measured_at")
        if not isinstance(document["tool"], str) or not document["tool"].strip():
            raise MasterProfileError("loudness evidence tool must be non-empty")
    else:
        if document["kind"] != "loudness_fixture":
            raise MasterProfileError("non-authoritative loudness evidence must use kind=loudness_fixture")
        if document["media_sha256"] is not None or document["measured_at"] is not None:
            raise MasterProfileError("loudness fixture cannot claim a media binding or measurement time")
    measurement = parse_loudness(document["measurement"])
    return measurement, authoritative, {
        key: document[key] for key in expected - {"measurement"}
    }


def _nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def tone_map_evidence_errors(
    evidence,
    *,
    project_id,
    video_id,
    source_sha256,
    output_sha256,
    source_profile_id,
    output_profile_id,
    not_before=None,
):
    errors = []
    if not isinstance(evidence, dict) or set(evidence) != TONE_MAP_REQUIRED_FIELDS:
        return [f"tone-map evidence fields must be exactly {sorted(TONE_MAP_REQUIRED_FIELDS)}"]
    expected = {
        "schema_version": "1.0.0",
        "kind": "hdr_to_sdr_tone_map",
        "project_id": project_id,
        "video_id": video_id,
        "source_sha256": source_sha256,
        "output_sha256": output_sha256,
        "source_profile_id": source_profile_id,
        "output_profile_id": output_profile_id,
    }
    for field, value in expected.items():
        if evidence.get(field) != value:
            errors.append(f"tone-map {field} does not match expected {value!r}")
    for field in ("tool", "tool_version", "method", "parameters"):
        if not _nonempty_text(evidence.get(field)):
            errors.append(f"tone-map {field} must be non-empty")
    performed_at = parse_rfc3339(evidence.get("performed_at"))
    if performed_at is None:
        errors.append("tone-map performed_at must be an RFC 3339 timestamp")
    else:
        if performed_at > datetime.now(timezone.utc):
            errors.append("tone-map performed_at cannot be in the future")
        if not_before is not None and performed_at < not_before:
            errors.append("tone-map performed_at cannot precede source approval")
    return errors


def visual_review_errors(
    review,
    *,
    project_id,
    video_id,
    output_sha256,
    profile_id,
    not_before=None,
):
    errors = []
    if not isinstance(review, dict) or set(review) != VISUAL_REVIEW_REQUIRED_FIELDS:
        return [f"visual review fields must be exactly {sorted(VISUAL_REVIEW_REQUIRED_FIELDS)}"]
    expected = {
        "schema_version": "1.0.0",
        "kind": "hdr_to_sdr_visual_review",
        "project_id": project_id,
        "video_id": video_id,
        "output_sha256": output_sha256,
        "profile_id": profile_id,
    }
    for field, value in expected.items():
        if review.get(field) != value:
            errors.append(f"visual review {field} does not match expected {value!r}")
    if not is_human_identity(review.get("reviewer")):
        errors.append("visual review requires an explicitly identified human reviewer")
    if not is_verifiable_human_reference("user_message", review.get("reference")):
        errors.append("visual review requires reference thread:<id>/turn:<id>")
    if not isinstance(review.get("note"), str):
        errors.append("visual review note must be a string")
    checks = review.get("checks")
    if not isinstance(checks, dict) or set(checks) != VISUAL_REVIEW_CHECKS:
        errors.append(f"visual review checks must be exactly {sorted(VISUAL_REVIEW_CHECKS)}")
    elif any(checks[name] is not True for name in VISUAL_REVIEW_CHECKS):
        errors.append("every visual review check must be explicitly true")
    reviewed_at = parse_rfc3339(review.get("reviewed_at"))
    if reviewed_at is None:
        errors.append("visual review reviewed_at must be an RFC 3339 timestamp")
    else:
        if reviewed_at > datetime.now(timezone.utc):
            errors.append("visual review reviewed_at cannot be in the future")
        if not_before is not None and reviewed_at < not_before:
            errors.append("visual review cannot precede tone mapping")
    return errors


def evaluate_profile(
    profile,
    metadata,
    *,
    media_path,
    media_sha256,
    probe_authoritative=True,
    probe_evidence=None,
    loudness=None,
    loudness_authoritative=True,
    loudness_evidence=None,
    approval_receipt=None,
    approval_receipt_path=None,
    source_master=None,
    source_profile=None,
    source_metadata=None,
    source_probe_authoritative=True,
    source_probe_evidence=None,
    expected_project_id=None,
    expected_video_id=None,
    tone_map_evidence=None,
    visual_review=None,
):
    profile_trust = _trusted_profile_entry(profile)
    if not isinstance(media_sha256, str) or not SHA256_PATTERN.fullmatch(media_sha256):
        raise MasterProfileError("media_sha256 must be a lowercase SHA-256")
    video = profile["video"]
    audio = profile["audio"]
    governance = profile["governance"]
    findings = []

    suffix = Path(media_path).suffix.lower()
    _allowed(findings, suffix, video["file_extensions"], "FILE_EXTENSION", "file extension")
    _allowed(findings, metadata.get("container"), video["containers"], "CONTAINER", "container")
    _allowed(findings, metadata.get("video_codec"), video["codecs"], "VIDEO_CODEC", "video codec")
    if video["codec_profiles"]:
        _allowed(findings, metadata.get("video_profile"), video["codec_profiles"], "VIDEO_PROFILE", "video profile")
    _allowed(findings, metadata.get("pixel_format"), video["pixel_formats"], "PIXEL_FORMAT", "pixel format")
    bit_depth = pixel_bit_depth(metadata.get("pixel_format"))
    if bit_depth is None or bit_depth < video["minimum_bit_depth"]:
        findings.append(
            _finding(
                "error",
                "BIT_DEPTH",
                f"bit depth: got {bit_depth!r}, expected at least {video['minimum_bit_depth']}",
            )
        )
    _equal(findings, metadata.get("width"), video["width"], "WIDTH", "width")
    _equal(findings, metadata.get("height"), video["height"], "HEIGHT", "height")
    _equal(
        findings,
        metadata.get("fps"),
        video["fps_target"],
        "FPS",
        "frame rate",
        tolerance=video["fps_tolerance"],
    )
    _equal(findings, metadata.get("orientation"), video["orientation"], "ORIENTATION", "orientation")
    _equal(findings, metadata.get("aspect_ratio"), video["aspect_ratio"], "ASPECT_RATIO", "aspect ratio")
    duration = metadata.get("duration_seconds")
    if duration is None or not video["duration_min_seconds"] <= duration <= video["duration_max_seconds"]:
        findings.append(
            _finding(
                "error",
                "DURATION",
                f"duration {duration!r}s is outside {video['duration_min_seconds']}..{video['duration_max_seconds']}s",
            )
        )
    _allowed(findings, metadata.get("color_primaries"), video["color_primaries"], "COLOR_PRIMARIES", "color primaries")
    _allowed(findings, metadata.get("color_transfer"), video["color_transfers"], "COLOR_TRANSFER", "color transfer")
    _allowed(findings, metadata.get("color_space"), video["color_spaces"], "COLOR_SPACE", "color space")

    bitrate = metadata.get("video_bitrate_bps")
    bitrate_severity = video["bitrate_enforcement"]
    if bitrate is None:
        findings.append(_finding("warning", "BITRATE_UNKNOWN", "ffprobe did not expose video bitrate"))
    else:
        bitrate_mbps = bitrate / 1_000_000
        if video["bitrate_min_mbps"] is not None and bitrate_mbps < video["bitrate_min_mbps"]:
            findings.append(
                _finding(
                    bitrate_severity,
                    "BITRATE_LOW",
                    f"video bitrate {bitrate_mbps:.2f} Mbps is below {video['bitrate_min_mbps']} Mbps",
                )
            )
        if video["bitrate_max_mbps"] is not None and bitrate_mbps > video["bitrate_max_mbps"]:
            findings.append(
                _finding(
                    bitrate_severity,
                    "BITRATE_HIGH",
                    f"video bitrate {bitrate_mbps:.2f} Mbps exceeds {video['bitrate_max_mbps']} Mbps",
                )
            )

    if audio["required"] and not metadata.get("audio_present"):
        findings.append(_finding("error", "AUDIO_MISSING", "profile requires an audio stream"))
    if metadata.get("audio_present"):
        _allowed(findings, metadata.get("audio_codec"), audio["codecs"], "AUDIO_CODEC", "audio codec")
        if audio["codec_profiles"]:
            _allowed(findings, metadata.get("audio_profile"), audio["codec_profiles"], "AUDIO_PROFILE", "audio profile")
        _equal(
            findings,
            metadata.get("audio_sample_rate_hz"),
            audio["sample_rate_hz"],
            "AUDIO_SAMPLE_RATE",
            "audio sample rate",
        )
        _equal(findings, metadata.get("audio_channels"), audio["channels"], "AUDIO_CHANNELS", "audio channels")

    if any(item["severity"] == "error" for item in findings):
        technical_status = "failed"
    elif not probe_authoritative:
        technical_status = "needs_evidence"
        findings.append(
            _finding(
                "warning",
                "NON_AUTHORITATIVE_PROBE",
                "fixture metadata cannot establish compliance for a real media artifact",
            )
        )
    else:
        technical_status = "passed"

    if audio["requires_loudness_scan"]:
        if loudness is None:
            loudness_status = "pending"
            findings.append(_finding("warning", "LOUDNESS_SCAN_REQUIRED", "attach a measured loudness result"))
        elif not loudness_authoritative:
            loudness_status = "pending"
            findings.append(
                _finding(
                    "warning",
                    "NON_AUTHORITATIVE_LOUDNESS",
                    "fixture loudness cannot establish compliance for a real media artifact",
                )
            )
        else:
            loudness_errors = False
            if abs(loudness["integrated_lufs"] - audio["target_lufs"]) > audio["lufs_tolerance"]:
                loudness_errors = True
                findings.append(
                    _finding(
                        "error",
                        "LOUDNESS_OUT_OF_RANGE",
                        f"integrated loudness {loudness['integrated_lufs']} LUFS is outside "
                        f"{audio['target_lufs']} ± {audio['lufs_tolerance']} LU",
                    )
                )
            if loudness["true_peak_dbtp"] > audio["true_peak_max_dbtp"]:
                loudness_errors = True
                findings.append(
                    _finding(
                        "error",
                        "TRUE_PEAK_TOO_HIGH",
                        f"true peak {loudness['true_peak_dbtp']} dBTP exceeds {audio['true_peak_max_dbtp']} dBTP",
                    )
                )
            loudness_status = "failed" if loudness_errors else "passed"
    else:
        loudness_status = "not_required"

    source_hash = None
    receipt_report = None
    source_profile_report = None
    if governance["requires_approved_source_receipt"]:
        if approval_receipt is None:
            lineage_status = "pending"
            findings.append(
                _finding(
                    "warning",
                    "APPROVED_SOURCE_REQUIRED",
                    "attach the receipt for the exact approved editorial source",
                )
            )
        else:
            resolved_source = resolve_artifact_path(
                approval_receipt,
                receipt_path=approval_receipt_path,
                artifact_override=source_master,
            )
            receipt_report = verify_receipt(
                approval_receipt,
                receipt_path=approval_receipt_path,
                artifact_override=resolved_source,
            )
            source_hash = receipt_report.get("actual_artifact_sha256")
            lineage_errors = []
            if not receipt_report["usable_as_approval"]:
                lineage_errors.append("source receipt is not a valid explicit approval bound to the source hash")
            artifact_contract = (
                approval_receipt.get("artifact")
                if isinstance(approval_receipt.get("artifact"), dict)
                else {}
            )
            decision_contract = (
                approval_receipt.get("decision")
                if isinstance(approval_receipt.get("decision"), dict)
                else {}
            )
            media_role = artifact_contract.get("media_role")
            if media_role != governance["required_source_media_role"]:
                lineage_errors.append(
                    f"source media role {media_role!r} does not match {governance['required_source_media_role']!r}"
                )
            required_source_profile = governance["required_source_profile_id"]
            if artifact_contract.get("profile_id") != required_source_profile:
                lineage_errors.append(
                    f"source profile {artifact_contract.get('profile_id')!r} does not match {required_source_profile!r}"
                )
            if expected_project_id is None or expected_video_id is None:
                lineage_errors.append("delivery lineage requires explicit project_id and video_id context")
            else:
                if approval_receipt.get("project_id") != expected_project_id:
                    lineage_errors.append("source receipt project_id does not match the delivery project")
                if approval_receipt.get("video_id") != expected_video_id:
                    lineage_errors.append("source receipt video_id does not match the delivery video")
            scope = decision_contract.get("scope", {})
            if scope.get("whole_artifact") is not True or scope.get("approved_layers"):
                lineage_errors.append("delivery requires whole-artifact source approval with no partial layer scope")
            if governance["source_hash_must_differ"] and source_hash == media_sha256:
                lineage_errors.append("delivery hash equals source hash; expected a distinct derived artifact")

            if source_profile is None or source_metadata is None or resolved_source is None:
                lineage_errors.append("source HDR profile and authoritative ffprobe evidence are required")
            else:
                try:
                    _trusted_profile_entry(source_profile)
                except MasterProfileError as error:
                    lineage_errors.append(str(error))
                else:
                    if source_profile["id"] != required_source_profile:
                        lineage_errors.append("loaded source profile does not match the required HDR profile")
                    if source_profile["artifact_role"] != "editorial_mezzanine":
                        lineage_errors.append("loaded source profile is not an editorial mezzanine profile")
                    if source_profile["color_intent"] != "preserve_hdr":
                        lineage_errors.append("loaded source profile does not preserve HDR")
                    if not source_probe_authoritative:
                        lineage_errors.append("source ffprobe fixture is non-authoritative")
                    source_profile_report = evaluate_profile(
                        source_profile,
                        source_metadata,
                        media_path=resolved_source,
                        media_sha256=source_hash,
                        probe_authoritative=source_probe_authoritative,
                        probe_evidence=source_probe_evidence,
                    )
                    if source_profile_report["technical_status"] != "passed":
                        lineage_errors.append("approved source does not comply with the trusted HDR profile")
            if lineage_errors:
                lineage_status = "failed"
                for message in lineage_errors:
                    findings.append(_finding("error", "SOURCE_LINEAGE_INVALID", message))
            else:
                lineage_status = "passed"
    else:
        lineage_status = "not_required"

    tone_map_status = "not_required"
    visual_review_status = "separate_required" if governance["requires_visual_review"] else "not_required"
    if profile["artifact_role"] == "social_delivery_master":
        approval_time = None
        if approval_receipt is not None:
            decision = (
                approval_receipt.get("decision")
                if isinstance(approval_receipt.get("decision"), dict)
                else {}
            )
            approval_time = parse_rfc3339(decision.get("decided_at"))
        if tone_map_evidence is None:
            tone_map_status = "pending"
            findings.append(_finding("warning", "TONE_MAP_EVIDENCE_REQUIRED", "attach HDR-to-SDR transform evidence"))
            tone_map_time = None
        else:
            tone_errors = tone_map_evidence_errors(
                tone_map_evidence,
                project_id=expected_project_id,
                video_id=expected_video_id,
                source_sha256=source_hash,
                output_sha256=media_sha256,
                source_profile_id=governance["required_source_profile_id"],
                output_profile_id=profile["id"],
                not_before=approval_time,
            )
            tone_map_status = "failed" if tone_errors else "passed"
            for message in tone_errors:
                findings.append(_finding("error", "TONE_MAP_EVIDENCE_INVALID", message))
            tone_map_time = parse_rfc3339(tone_map_evidence.get("performed_at"))

        if visual_review is None:
            visual_review_status = "pending"
            findings.append(
                _finding(
                    "warning",
                    "HDR_SDR_VISUAL_REVIEW_REQUIRED",
                    "attach a human visual review bound to the delivery hash",
                )
            )
        else:
            review_errors = visual_review_errors(
                visual_review,
                project_id=expected_project_id,
                video_id=expected_video_id,
                output_sha256=media_sha256,
                profile_id=profile["id"],
                not_before=tone_map_time,
            )
            visual_review_status = "failed" if review_errors else "passed"
            for message in review_errors:
                findings.append(_finding("error", "HDR_SDR_VISUAL_REVIEW_INVALID", message))

    statuses = {
        technical_status,
        loudness_status,
        lineage_status,
        tone_map_status,
        visual_review_status,
    }
    if "failed" in statuses:
        profile_status = "failed"
    elif "pending" in statuses or "needs_evidence" in statuses:
        profile_status = "needs_evidence"
    else:
        profile_status = "compliant"
    visual_review_required = governance["requires_visual_review"]
    return {
        "schema_version": "1.0.0",
        "profile_id": profile["id"],
        "profile_version": profile["profile_version"],
        "profile_sha256": profile_trust["file_sha256"],
        "artifact_role": profile["artifact_role"],
        "color_intent": profile["color_intent"],
        "media_path": str(media_path),
        "media_sha256": media_sha256,
        "source_sha256": source_hash,
        "inspected_at": utc_now(),
        "technical_status": technical_status,
        "loudness_status": loudness_status,
        "lineage_status": lineage_status,
        "tone_map_status": tone_map_status,
        "visual_review_status": visual_review_status,
        "profile_status": profile_status,
        "visual_review_required": visual_review_required,
        "publication_ready": (
            profile_status == "compliant"
            and (not visual_review_required or visual_review_status == "passed")
        ),
        "status_notice": (
            "SHA-256 and transform records establish integrity and declared lineage, not cryptographic identity. "
            "Human references must be checked independently."
        ),
        "metadata": metadata,
        "probe_evidence": probe_evidence,
        "loudness": loudness,
        "loudness_evidence": loudness_evidence,
        "approval_receipt_verification": receipt_report,
        "source_profile_verification": source_profile_report,
        "source_probe_evidence": source_probe_evidence,
        "tone_map_evidence": tone_map_evidence,
        "visual_review": visual_review,
        "findings": findings,
    }


def _emit_report(report, out=None, write=False):
    if out is not None and not write:
        raise MasterProfileError("--out requires explicit --write; default operation is read-only")
    if write and out is None:
        raise MasterProfileError("--write requires --out")
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if out is not None:
        atomic_write_text(out, encoded)
    print(encoded, end="")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--media", type=Path, required=True)
    parser.add_argument("--probe-json", type=Path, help="hash-bound ffprobe evidence envelope")
    parser.add_argument("--loudness-json", type=Path, help="hash-bound loudness evidence envelope")
    parser.add_argument("--project-id", help="required delivery context for social masters")
    parser.add_argument("--video-id", help="required delivery context for social masters")
    parser.add_argument("--source-master", type=Path)
    parser.add_argument("--source-probe-json", type=Path, help="hash-bound source ffprobe evidence envelope")
    parser.add_argument("--approval-receipt", type=Path)
    parser.add_argument("--tone-map-json", type=Path, help="HDR-to-SDR transform evidence")
    parser.add_argument("--visual-review-json", type=Path, help="human HDR-to-SDR visual review")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--write", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        media_fingerprint = file_fingerprint(args.media)
        profile = load_profile(args.profile)
        if args.probe_json:
            probe, probe_authoritative, probe_evidence = load_probe_evidence(
                args.probe_json,
                media_fingerprint["sha256"],
            )
        else:
            probe = run_ffprobe(args.media, args.ffprobe)
            probe_authoritative = True
            probe_evidence = {
                "kind": "live_ffprobe",
                "authoritative": True,
                "media_sha256": media_fingerprint["sha256"],
                "tool": args.ffprobe,
            }
        metadata = parse_ffprobe(probe)
        if args.loudness_json:
            loudness, loudness_authoritative, loudness_evidence = load_loudness_evidence(
                args.loudness_json,
                media_fingerprint["sha256"],
            )
        else:
            loudness = None
            loudness_authoritative = False
            loudness_evidence = None
        receipt = load_json(args.approval_receipt, "approval receipt") if args.approval_receipt else None
        source_path = (
            resolve_artifact_path(receipt, args.approval_receipt, args.source_master)
            if receipt is not None
            else args.source_master
        )
        source_profile = None
        source_metadata = None
        source_probe_authoritative = False
        source_probe_evidence = None
        if profile["governance"]["requires_approved_source_receipt"] and source_path is not None:
            required_source_id = profile["governance"]["required_source_profile_id"]
            source_entry = TRUSTED_PROFILE_REGISTRY[required_source_id]
            source_profile = load_profile(FRAMEWORK_ROOT / source_entry["relative_path"])
            source_fingerprint = file_fingerprint(source_path)
            if args.source_probe_json:
                source_probe, source_probe_authoritative, source_probe_evidence = load_probe_evidence(
                    args.source_probe_json,
                    source_fingerprint["sha256"],
                    label="source probe evidence",
                )
            else:
                source_probe = run_ffprobe(source_path, args.ffprobe)
                source_probe_authoritative = True
                source_probe_evidence = {
                    "kind": "live_ffprobe",
                    "authoritative": True,
                    "media_sha256": source_fingerprint["sha256"],
                    "tool": args.ffprobe,
                }
            source_metadata = parse_ffprobe(source_probe)
        tone_map_evidence = load_json(args.tone_map_json, "tone-map evidence") if args.tone_map_json else None
        visual_review = load_json(args.visual_review_json, "HDR-to-SDR visual review") if args.visual_review_json else None
        result = evaluate_profile(
            profile,
            metadata,
            media_path=args.media,
            media_sha256=media_fingerprint["sha256"],
            probe_authoritative=probe_authoritative,
            probe_evidence=probe_evidence,
            loudness=loudness,
            loudness_authoritative=loudness_authoritative,
            loudness_evidence=loudness_evidence,
            approval_receipt=receipt,
            approval_receipt_path=args.approval_receipt,
            source_master=source_path,
            source_profile=source_profile,
            source_metadata=source_metadata,
            source_probe_authoritative=source_probe_authoritative,
            source_probe_evidence=source_probe_evidence,
            expected_project_id=args.project_id,
            expected_video_id=args.video_id,
            tone_map_evidence=tone_map_evidence,
            visual_review=visual_review,
        )
        _emit_report(result, args.out, args.write)
        if result["profile_status"] == "compliant":
            return 0
        if result["profile_status"] == "needs_evidence":
            return 4
        return 3
    except (
        ApprovalReceiptError,
        DeliveryCheckError,
        MasterProfileError,
        OSError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
