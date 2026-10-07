#!/usr/bin/env python3
"""Preflight one encoded derivative against a platform profile and signed preview review."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from math import gcd, isfinite
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from plan_platform_derivatives import (  # noqa: E402
    DEFAULT_CATALOG,
    PlatformPlanError,
    atomic_write_json,
    load_catalog,
    read_json,
)


REVIEW_CHECKS = (
    "live_preview_on_target_surface",
    "essential_content_inside_safe_zone",
    "captions_legible_and_unobstructed",
    "cta_legible_and_unobstructed",
    "face_not_obscured",
    "content_semantics_unchanged",
)
SHA256 = re.compile(r"^[a-f0-9]{64}$")
RFC3339 = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)


class DeliveryCheckError(ValueError):
    """Delivery input, probe data, or review evidence is malformed."""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_ffprobe(media_path, executable="ffprobe"):
    command = [
        executable,
        "-v",
        "error",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(media_path),
    ]
    try:
        process = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as error:
        raise DeliveryCheckError(f"ffprobe executable not found: {executable}") from error
    if process.returncode != 0:
        detail = process.stderr.strip() or f"exit code {process.returncode}"
        raise DeliveryCheckError(f"ffprobe failed for {media_path}: {detail}")
    try:
        return json.loads(process.stdout)
    except json.JSONDecodeError as error:
        raise DeliveryCheckError(f"ffprobe returned invalid JSON: {error}") from error


def _number(value, label, allow_none=True):
    if value in (None, "", "N/A") and allow_none:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise DeliveryCheckError(f"{label} must be numeric, got {value!r}") from error
    if not isfinite(result):
        raise DeliveryCheckError(f"{label} must be finite, got {value!r}")
    if result < 0:
        raise DeliveryCheckError(f"{label} cannot be negative")
    return result


def _integer(value, label, allow_none=True):
    result = _number(value, label, allow_none=allow_none)
    if result is None:
        return None
    if not result.is_integer():
        raise DeliveryCheckError(f"{label} must be an integer, got {value!r}")
    return int(result)


def _fps(value):
    if value in (None, "", "0/0", "N/A"):
        return None
    try:
        rate = Fraction(str(value))
    except (ValueError, ZeroDivisionError) as error:
        raise DeliveryCheckError(f"invalid frame rate {value!r}") from error
    return float(rate)


def _container(format_name):
    names = {item.strip().lower() for item in str(format_name or "").split(",") if item.strip()}
    if "mp4" in names:
        return "mp4"
    if "mov" in names:
        return "mov"
    return sorted(names)[0] if names else "unknown"


def _aspect_ratio(width, height):
    if not width or not height:
        return "unknown"
    divisor = gcd(int(width), int(height))
    return f"{int(width) // divisor}:{int(height) // divisor}"


def _orientation(width, height):
    if not width or not height:
        return "unknown"
    if width == height:
        return "square"
    return "vertical" if height > width else "horizontal"


def parse_ffprobe(probe):
    if not isinstance(probe, dict):
        raise DeliveryCheckError("ffprobe document must be an object")
    streams = probe.get("streams")
    if not isinstance(streams, list):
        raise DeliveryCheckError("ffprobe document is missing streams")
    video = next((item for item in streams if item.get("codec_type") == "video"), None)
    audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    if video is None:
        raise DeliveryCheckError("delivery has no video stream")
    width = _integer(video.get("width"), "video width", allow_none=False)
    height = _integer(video.get("height"), "video height", allow_none=False)
    rate = _fps(video.get("avg_frame_rate") or video.get("r_frame_rate"))
    format_data = probe.get("format") if isinstance(probe.get("format"), dict) else {}
    duration = _number(video.get("duration"), "video duration")
    if duration is None:
        duration = _number(format_data.get("duration"), "format duration", allow_none=False)
    bitrate = _integer(video.get("bit_rate"), "video bitrate")
    if bitrate is None:
        bitrate = _integer(format_data.get("bit_rate"), "format bitrate")
    audio_rate = _integer(audio.get("sample_rate"), "audio sample rate") if audio else None
    channels = _integer(audio.get("channels"), "audio channels") if audio else None
    return {
        "width": width,
        "height": height,
        "fps": rate,
        "aspect_ratio": _aspect_ratio(width, height),
        "orientation": _orientation(width, height),
        "duration_seconds": duration,
        "container": _container(format_data.get("format_name")),
        "video_codec": str(video.get("codec_name") or "unknown").lower(),
        "video_profile": str(video.get("profile") or "unknown").lower(),
        "pixel_format": str(video.get("pix_fmt") or "unknown").lower(),
        "video_bitrate_bps": bitrate,
        "color_primaries": str(video.get("color_primaries") or "unknown").lower(),
        "color_transfer": str(video.get("color_transfer") or "unknown").lower(),
        "color_space": str(video.get("color_space") or "unknown").lower(),
        "audio_present": audio is not None,
        "audio_codec": str(audio.get("codec_name") or "unknown").lower() if audio else "missing",
        "audio_profile": str(audio.get("profile") or "unknown").lower() if audio else "missing",
        "audio_sample_rate_hz": audio_rate,
        "audio_channels": channels,
    }


def _finding(severity, code, message, source_url=None, scope=None):
    result = {"severity": severity, "code": code, "message": message}
    if source_url:
        result["source_url"] = source_url
    if scope:
        result["scope"] = scope
    return result


def _compare(findings, actual, expected, code, label, severity="error", tolerance=None):
    if tolerance is None:
        matches = str(actual).lower() == str(expected).lower()
    else:
        matches = actual is not None and abs(float(actual) - float(expected)) <= tolerance
    if not matches:
        findings.append(_finding(severity, code, f"{label}: got {actual!r}, expected {expected!r}"))


def _official_constraint_result(constraint, metadata):
    field = constraint["field"]
    actual = metadata.get(field)
    operator = constraint["operator"]
    if operator == "minimum":
        passed = actual is not None and float(actual) >= float(constraint["number_value"])
        expected = f">= {constraint['number_value']}"
    elif operator == "maximum":
        passed = actual is not None and float(actual) <= float(constraint["number_value"])
        expected = f"<= {constraint['number_value']}"
    elif operator == "one_of":
        passed = str(actual).lower() in {item.lower() for item in constraint["string_values"]}
        expected = f"one of {constraint['string_values']}"
    else:
        if constraint["number_value"] is not None:
            passed = actual is not None and abs(float(actual) - float(constraint["number_value"])) <= 0.01
            expected = str(constraint["number_value"])
        else:
            expected_value = constraint["string_values"][0]
            passed = str(actual).lower() == expected_value.lower()
            expected = expected_value
    return passed, actual, expected


def _validate_review(review, profile_id, media_sha256):
    expected = {
        "schema_version",
        "profile_id",
        "output_sha256",
        "reviewer",
        "reviewed_at",
        "preview_context",
        "checks",
        "note",
    }
    if not isinstance(review, dict) or set(review) != expected:
        raise DeliveryCheckError(f"review fields must be exactly {sorted(expected)}")
    if review["schema_version"] != "1.0.0":
        raise DeliveryCheckError("unsupported review schema_version")
    if review["profile_id"] != profile_id:
        raise DeliveryCheckError("review profile_id does not match requested profile")
    if not isinstance(review["output_sha256"], str) or not SHA256.fullmatch(review["output_sha256"]):
        raise DeliveryCheckError("review output_sha256 must be a lowercase SHA-256")
    if media_sha256 and review["output_sha256"] != media_sha256:
        raise DeliveryCheckError("review output_sha256 does not match the encoded delivery")
    for field in ("reviewer", "preview_context"):
        if not isinstance(review[field], str) or not review[field].strip():
            raise DeliveryCheckError(f"review {field} must be non-empty")
    if not isinstance(review["reviewed_at"], str) or not RFC3339.fullmatch(review["reviewed_at"]):
        raise DeliveryCheckError("review reviewed_at must be an RFC 3339 timestamp")
    try:
        datetime.fromisoformat(review["reviewed_at"].replace("Z", "+00:00"))
    except ValueError as error:
        raise DeliveryCheckError("review reviewed_at is not a valid timestamp") from error
    if not isinstance(review["note"], str):
        raise DeliveryCheckError("review note must be a string")
    checks = review["checks"]
    if not isinstance(checks, dict) or set(checks) != set(REVIEW_CHECKS):
        raise DeliveryCheckError(f"review checks must be exactly {sorted(REVIEW_CHECKS)}")
    if not all(isinstance(value, bool) for value in checks.values()):
        raise DeliveryCheckError("every review check must be boolean")
    return all(checks.values()), [name for name, passed in checks.items() if not passed]


def evaluate_delivery(profile, metadata, review=None, media_sha256=None, media_path=""):
    if profile["kind"] != "derivative":
        raise DeliveryCheckError("delivery checks require a derivative platform profile")
    defaults = profile["internal_defaults"]
    canvas = defaults["canvas"]
    video = defaults["video"]
    audio = defaults["audio"]
    duration = defaults["duration"]
    findings = []

    _compare(findings, metadata.get("width"), canvas["width"], "INTERNAL_WIDTH", "width")
    _compare(findings, metadata.get("height"), canvas["height"], "INTERNAL_HEIGHT", "height")
    _compare(
        findings,
        metadata.get("fps"),
        canvas["fps"],
        "INTERNAL_FPS",
        "frame rate",
        tolerance=0.02,
    )
    _compare(findings, metadata.get("container"), video["container"], "INTERNAL_CONTAINER", "container")
    _compare(findings, metadata.get("video_codec"), video["codec"], "INTERNAL_VIDEO_CODEC", "video codec")
    _compare(findings, metadata.get("pixel_format"), video["pixel_format"], "INTERNAL_PIXEL_FORMAT", "pixel format")
    _compare(findings, metadata.get("color_primaries"), video["color_primaries"], "INTERNAL_COLOR_PRIMARIES", "color primaries")
    _compare(findings, metadata.get("color_transfer"), video["color_transfer"], "INTERNAL_COLOR_TRANSFER", "color transfer")
    _compare(findings, metadata.get("color_space"), video["color_space"], "INTERNAL_COLOR_SPACE", "color space")
    _compare(findings, metadata.get("audio_codec"), audio["codec"], "INTERNAL_AUDIO_CODEC", "audio codec")
    _compare(
        findings,
        metadata.get("audio_sample_rate_hz"),
        audio["sample_rate_hz"],
        "INTERNAL_AUDIO_RATE",
        "audio sample rate",
    )
    if metadata.get("audio_channels") != audio["channels"]:
        findings.append(
            _finding(
                "warning",
                "INTERNAL_AUDIO_CHANNELS",
                f"audio channels: got {metadata.get('audio_channels')!r}, preferred {audio['channels']!r}",
            )
        )
    actual_duration = metadata.get("duration_seconds")
    if actual_duration is None or not duration["workflow_min_seconds"] <= actual_duration <= duration["workflow_max_seconds"]:
        findings.append(
            _finding(
                "error",
                "INTERNAL_DURATION",
                f"duration {actual_duration!r}s is outside internal workflow range "
                f"{duration['workflow_min_seconds']}..{duration['workflow_max_seconds']}s",
            )
        )
    bitrate = metadata.get("video_bitrate_bps")
    if bitrate is None:
        findings.append(_finding("warning", "BITRATE_UNKNOWN", "ffprobe did not expose a video bitrate"))
    elif bitrate < video["target_bitrate_mbps"] * 1_000_000 * 0.75:
        findings.append(
            _finding(
                "warning",
                "BITRATE_BELOW_TARGET",
                f"video bitrate {bitrate / 1_000_000:.2f} Mbps is below 75% of the {video['target_bitrate_mbps']} Mbps target",
            )
        )

    for constraint in profile["official_constraints"]["automated_constraints"]:
        passed, actual, expected = _official_constraint_result(constraint, metadata)
        if not passed:
            severity = "error" if constraint["enforcement"] == "hard" else "warning"
            findings.append(
                _finding(
                    severity,
                    f"OFFICIAL_{constraint['id'].upper()}",
                    f"official-scope check {constraint['field']}: got {actual!r}, expected {expected}",
                    source_url=constraint["source_url"],
                    scope=constraint["scope"],
                )
            )

    technical_status = "failed" if any(item["severity"] == "error" for item in findings) else "passed"
    if review is None:
        manual_status = "pending"
        findings.append(
            _finding(
                "warning",
                "LIVE_PREVIEW_REQUIRED",
                "safe zones are conservative internal guides; attach a hash-bound live-platform preview review",
            )
        )
    else:
        review_passed, failed_checks = _validate_review(review, profile["id"], media_sha256)
        if review_passed:
            manual_status = "passed"
        else:
            manual_status = "failed"
            findings.append(
                _finding(
                    "error",
                    "MANUAL_REVIEW_FAILED",
                    "manual preview checks failed: " + ", ".join(failed_checks),
                )
            )

    if technical_status == "failed" or manual_status == "failed":
        delivery_status = "failed"
    elif manual_status == "pending":
        delivery_status = "needs_manual_preview"
    else:
        delivery_status = "ready"
    return {
        "schema_version": "1.0.0",
        "profile_id": profile["id"],
        "platform": profile["platform"],
        "surface": profile["surface"],
        "media_path": str(media_path),
        "media_sha256": media_sha256,
        "inspected_at": utc_now(),
        "safe_zone_provenance": profile["internal_defaults"]["safe_zones"]["provenance"],
        "technical_status": technical_status,
        "manual_review_status": manual_status,
        "delivery_status": delivery_status,
        "metadata": metadata,
        "findings": findings,
    }


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--media", type=Path, required=True)
    parser.add_argument("--probe-json", type=Path, help="use saved ffprobe JSON instead of invoking ffprobe")
    parser.add_argument("--review", type=Path, help="hash-bound manual platform preview review JSON")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--out", type=Path)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if not args.media.is_file():
            raise DeliveryCheckError(f"media file does not exist: {args.media}")
        catalog = load_catalog(args.catalog)
        profile = next((item for item in catalog["profiles"] if item["id"] == args.profile), None)
        if profile is None:
            raise DeliveryCheckError(f"unknown platform profile {args.profile}")
        probe = read_json(args.probe_json, "ffprobe fixture") if args.probe_json else run_ffprobe(args.media, args.ffprobe)
        metadata = parse_ffprobe(probe)
        media_hash = sha256_file(args.media)
        review = read_json(args.review, "platform review") if args.review else None
        result = evaluate_delivery(profile, metadata, review, media_hash, args.media)
        if args.out:
            atomic_write_json(args.out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result["delivery_status"] == "ready":
            return 0
        if result["delivery_status"] == "needs_manual_preview":
            return 4
        return 3
    except (DeliveryCheckError, PlatformPlanError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
