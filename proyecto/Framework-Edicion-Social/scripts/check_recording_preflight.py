#!/usr/bin/env python3
"""Run an initial, read-only ffprobe preflight against a recording policy."""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


POLICY_FIELDS = {
    "require_audio",
    "allowed_video_codecs",
    "allowed_audio_codecs",
    "min_short_edge_px",
    "min_long_edge_px",
    "min_duration_s",
    "min_fps",
    "max_fps",
    "min_audio_sample_rate_hz",
    "min_audio_channels",
    "allowed_orientations",
    "vfr_warn_delta_fps",
    "warn_on_missing_color_metadata",
}


class PreflightError(ValueError):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as error:
        raise PreflightError(f"invalid preflight configuration JSON: {error}") from error


def validate_config(config):
    if not isinstance(config, dict):
        raise PreflightError("preflight configuration must be an object")
    if config.get("schema_version") != "1.0.0":
        raise PreflightError("unsupported recording-preflight schema_version")
    policy = config.get("policy")
    if not isinstance(policy, dict) or set(policy) != POLICY_FIELDS:
        raise PreflightError(f"policy fields must be exactly {sorted(POLICY_FIELDS)}")
    if not isinstance(policy["require_audio"], bool) or not isinstance(policy["warn_on_missing_color_metadata"], bool):
        raise PreflightError("boolean policy fields are invalid")
    for field in ("allowed_video_codecs", "allowed_audio_codecs", "allowed_orientations"):
        value = policy[field]
        if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
            raise PreflightError(f"{field} must be a non-empty string array")
        if len(value) != len(set(value)):
            raise PreflightError(f"{field} must not contain duplicates")
    if not set(policy["allowed_orientations"]) <= {"portrait", "landscape", "square"}:
        raise PreflightError("allowed_orientations contains an unsupported value")
    integer_fields = ("min_short_edge_px", "min_long_edge_px", "min_audio_sample_rate_hz", "min_audio_channels")
    for field in integer_fields:
        value = policy[field]
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise PreflightError(f"{field} must be a positive integer")
    numeric_fields = ("min_duration_s", "min_fps", "max_fps", "vfr_warn_delta_fps")
    for field in numeric_fields:
        value = policy[field]
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise PreflightError(f"{field} must be a non-negative number")
    if policy["min_fps"] <= 0 or policy["max_fps"] < policy["min_fps"]:
        raise PreflightError("fps range is invalid")
    return config


def run_ffprobe(source, timeout=20):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        "-print_format",
        "json",
        str(source),
    ]
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise PreflightError(f"ffprobe could not run: {error}") from error
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"exit code {completed.returncode}"
        raise PreflightError(f"ffprobe failed: {detail}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise PreflightError(f"ffprobe returned invalid JSON: {error}") from error


def rational(value):
    if not isinstance(value, str) or value in {"", "0/0", "N/A"}:
        return None
    try:
        result = float(Fraction(value))
    except (ValueError, ZeroDivisionError):
        return None
    return result if result >= 0 else None


def integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def number(value):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result >= 0 else None


def stream_rotation(stream):
    tags = stream.get("tags", {}) if isinstance(stream.get("tags"), dict) else {}
    raw = tags.get("rotate")
    if raw is None:
        for item in stream.get("side_data_list", []):
            if isinstance(item, dict) and "rotation" in item:
                raw = item["rotation"]
                break
    try:
        return int(round(float(raw))) if raw is not None else 0
    except (TypeError, ValueError):
        return 0


def orientation(width, height):
    if not width or not height:
        return None
    if width == height:
        return "square"
    return "portrait" if height > width else "landscape"


def summarize_probe(raw):
    if not isinstance(raw, dict):
        raise PreflightError("ffprobe result must be an object")
    streams = raw.get("streams", [])
    if not isinstance(streams, list):
        raise PreflightError("ffprobe streams must be an array")
    videos = [item for item in streams if isinstance(item, dict) and item.get("codec_type") == "video"]
    audios = [item for item in streams if isinstance(item, dict) and item.get("codec_type") == "audio"]
    video = videos[0] if videos else None
    audio = audios[0] if audios else None
    video_summary = None
    if video:
        width = integer(video.get("width"))
        height = integer(video.get("height"))
        rotation = stream_rotation(video)
        display_width, display_height = width, height
        if width and height and abs(rotation) % 180 == 90:
            display_width, display_height = height, width
        video_summary = {
            "codec": video.get("codec_name") if isinstance(video.get("codec_name"), str) else None,
            "coded_width": width,
            "coded_height": height,
            "display_width": display_width,
            "display_height": display_height,
            "rotation_degrees": rotation,
            "orientation": orientation(display_width, display_height),
            "avg_fps": rational(video.get("avg_frame_rate")),
            "nominal_fps": rational(video.get("r_frame_rate")),
            "color_space": video.get("color_space") if isinstance(video.get("color_space"), str) else None,
            "color_transfer": video.get("color_transfer") if isinstance(video.get("color_transfer"), str) else None,
            "color_primaries": video.get("color_primaries") if isinstance(video.get("color_primaries"), str) else None,
        }
    audio_summary = None
    if audio:
        audio_summary = {
            "codec": audio.get("codec_name") if isinstance(audio.get("codec_name"), str) else None,
            "sample_rate_hz": integer(audio.get("sample_rate")),
            "channels": integer(audio.get("channels")),
            "channel_layout": audio.get("channel_layout") if isinstance(audio.get("channel_layout"), str) else None,
        }
    format_data = raw.get("format", {}) if isinstance(raw.get("format"), dict) else {}
    return {
        "format_name": format_data.get("format_name") if isinstance(format_data.get("format_name"), str) else None,
        "duration_s": number(format_data.get("duration")),
        "size_bytes": integer(format_data.get("size")),
        "video_stream_count": len(videos),
        "audio_stream_count": len(audios),
        "video": video_summary,
        "audio": audio_summary,
    }


def _check(checks, check_id, name, severity, status, observed, expected, message=""):
    checks.append(
        {
            "id": check_id,
            "name": name,
            "severity": severity,
            "status": status,
            "observed": str(observed),
            "expected": str(expected),
            "message": message,
        }
    )


def _not_run(checks, check_id, name, severity, expected, message):
    _check(checks, check_id, name, severity, "not_run", "unavailable", expected, message)


def build_report(source, config, raw_probe=None, probe_error=None):
    validate_config(config)
    source = Path(source).expanduser().resolve()
    policy = copy.deepcopy(config["policy"])
    checks = []
    exists = source.is_file()
    _check(
        checks,
        "PF-001",
        "source file",
        "hard",
        "pass" if exists else "fail",
        "readable file" if exists else "missing",
        "readable regular file",
        "" if exists else f"source does not exist: {source}",
    )
    probe = None
    if not exists:
        _not_run(checks, "PF-002", "ffprobe", "hard", "successful media probe", "source is unavailable")
    elif probe_error is not None:
        _check(checks, "PF-002", "ffprobe", "hard", "fail", str(probe_error), "successful media probe", str(probe_error))
    else:
        try:
            probe = summarize_probe(raw_probe)
        except PreflightError as error:
            probe_error = error
            _check(checks, "PF-002", "ffprobe", "hard", "fail", str(error), "successful media probe", str(error))
        else:
            _check(checks, "PF-002", "ffprobe", "hard", "pass", "valid JSON", "successful media probe")

    if probe is not None:
        video = probe["video"]
        audio = probe["audio"]
        _check(
            checks,
            "PF-003",
            "video stream",
            "hard",
            "pass" if video else "fail",
            probe["video_stream_count"],
            "at least 1",
            "" if video else "no video stream was detected",
        )
        duration = probe["duration_s"]
        duration_ok = duration is not None and duration >= policy["min_duration_s"]
        _check(
            checks,
            "PF-004",
            "duration",
            "hard",
            "pass" if duration_ok else "fail",
            duration,
            f">= {policy['min_duration_s']} s",
            "" if duration_ok else "duration is missing or below minimum",
        )
        audio_ok = audio is not None or not policy["require_audio"]
        _check(
            checks,
            "PF-005",
            "audio stream",
            "hard",
            "pass" if audio_ok else "fail",
            probe["audio_stream_count"],
            "at least 1" if policy["require_audio"] else "optional",
            "" if audio_ok else "required audio stream is missing",
        )

        if video:
            short_edge = min(video["display_width"] or 0, video["display_height"] or 0)
            long_edge = max(video["display_width"] or 0, video["display_height"] or 0)
            resolution_ok = short_edge >= policy["min_short_edge_px"] and long_edge >= policy["min_long_edge_px"]
            _check(
                checks,
                "PF-006",
                "display resolution",
                "hard",
                "pass" if resolution_ok else "fail",
                f"{video['display_width']}x{video['display_height']}",
                f"short >= {policy['min_short_edge_px']}, long >= {policy['min_long_edge_px']}",
                "" if resolution_ok else "display resolution is below policy",
            )
            fps = video["avg_fps"]
            fps_ok = fps is not None and policy["min_fps"] <= fps <= policy["max_fps"]
            _check(
                checks,
                "PF-007",
                "average frame rate",
                "hard",
                "pass" if fps_ok else "fail",
                fps,
                f"{policy['min_fps']}..{policy['max_fps']} fps",
                "" if fps_ok else "average frame rate is missing or outside policy",
            )
            codec_ok = video["codec"] in policy["allowed_video_codecs"]
            _check(checks, "PF-008", "video codec", "hard", "pass" if codec_ok else "fail", video["codec"], policy["allowed_video_codecs"], "" if codec_ok else "video codec is not allowed")
            orientation_ok = video["orientation"] in policy["allowed_orientations"]
            _check(checks, "PF-009", "orientation", "hard", "pass" if orientation_ok else "fail", video["orientation"], policy["allowed_orientations"], "" if orientation_ok else "display orientation is not allowed")
            nominal = video["nominal_fps"]
            drift = abs(nominal - fps) if nominal is not None and fps is not None else None
            vfr_ok = drift is not None and drift <= policy["vfr_warn_delta_fps"]
            _check(
                checks,
                "PF-010",
                "frame-rate drift",
                "advisory",
                "pass" if vfr_ok else "warn",
                drift,
                f"<= {policy['vfr_warn_delta_fps']} fps",
                "" if vfr_ok else "nominal and average frame rates differ or are unavailable; edit by time, not frame count",
            )
            color_complete = all(video[field] for field in ("color_space", "color_transfer", "color_primaries"))
            color_status = "pass" if color_complete or not policy["warn_on_missing_color_metadata"] else "warn"
            _check(
                checks,
                "PF-011",
                "color metadata",
                "advisory",
                color_status,
                "/".join(str(video[field]) for field in ("color_space", "color_transfer", "color_primaries")),
                "space/transfer/primaries declared",
                "" if color_status == "pass" else "color metadata is incomplete",
            )

        if audio:
            codec_ok = audio["codec"] in policy["allowed_audio_codecs"]
            _check(checks, "PF-012", "audio codec", "hard", "pass" if codec_ok else "fail", audio["codec"], policy["allowed_audio_codecs"], "" if codec_ok else "audio codec is not allowed")
            sample_ok = audio["sample_rate_hz"] is not None and audio["sample_rate_hz"] >= policy["min_audio_sample_rate_hz"]
            _check(checks, "PF-013", "audio sample rate", "hard", "pass" if sample_ok else "fail", audio["sample_rate_hz"], f">= {policy['min_audio_sample_rate_hz']} Hz", "" if sample_ok else "audio sample rate is below policy")
            channels_ok = audio["channels"] is not None and audio["channels"] >= policy["min_audio_channels"]
            _check(checks, "PF-014", "audio channels", "hard", "pass" if channels_ok else "fail", audio["channels"], f">= {policy['min_audio_channels']}", "" if channels_ok else "audio channel count is below policy")

    counts = {status: sum(item["status"] == status for item in checks) for status in ("pass", "warn", "fail", "not_run")}
    overall = "fail" if counts["fail"] else "warn" if counts["warn"] else "pass" if checks else "pending"
    return {
        "schema_version": "1.0.0",
        "project_id": config.get("project_id", ""),
        "recording_id": config.get("recording_id") or source.stem,
        "source_path": str(source),
        "policy": policy,
        "probe": probe,
        "checks": checks,
        "summary": {
            "status": overall,
            **counts,
            "delivery_ready": overall in {"pass", "warn"},
        },
        "checked_at": utc_now(),
    }


def run_preflight(source, config, timeout=20, probe_runner=run_ffprobe):
    validate_config(config)
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        return build_report(source, config)
    try:
        raw = probe_runner(source, timeout=timeout)
    except PreflightError as error:
        return build_report(source, config, probe_error=error)
    return build_report(source, config, raw_probe=raw)


def atomic_write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def main(argv=None):
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--config", type=Path, default=root / "templates/recording-preflight.json")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = run_preflight(args.source, read_json(args.config), timeout=args.timeout)
        if args.out:
            atomic_write_json(args.out, report)
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            summary = report["summary"]
            print(
                f"recording preflight: {summary['status']} "
                f"(pass={summary['pass']} warn={summary['warn']} fail={summary['fail']} not_run={summary['not_run']})"
            )
        return 1 if report["summary"]["status"] == "fail" else 0
    except (PreflightError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
