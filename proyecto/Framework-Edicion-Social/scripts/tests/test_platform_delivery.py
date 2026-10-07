#!/usr/bin/env python3

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path


FRAMEWORK = Path(__file__).resolve().parents[2]
SCRIPT_DIR = FRAMEWORK / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
SCRIPT = SCRIPT_DIR / "check_platform_delivery.py"
SPEC = importlib.util.spec_from_file_location("check_platform_delivery", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CATALOG = MODULE.load_catalog(FRAMEWORK / "platforms/catalog.json")


def profile(profile_id="PLATFORM-YOUTUBE-SHORTS-001"):
    return next(item for item in CATALOG["profiles"] if item["id"] == profile_id)


def probe(duration="60.0"):
    return {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "h264",
                "profile": "High",
                "width": 1080,
                "height": 1920,
                "pix_fmt": "yuv420p",
                "avg_frame_rate": "30/1",
                "duration": duration,
                "bit_rate": "8000000",
                "color_primaries": "bt709",
                "color_transfer": "bt709",
                "color_space": "bt709",
            },
            {
                "codec_type": "audio",
                "codec_name": "aac",
                "profile": "LC",
                "sample_rate": "48000",
                "channels": 2,
            },
        ],
        "format": {
            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            "duration": duration,
            "bit_rate": "8200000",
        },
    }


def review(profile_id, media_hash, **check_overrides):
    checks = {name: True for name in MODULE.REVIEW_CHECKS}
    checks.update(check_overrides)
    return {
        "schema_version": "1.0.0",
        "profile_id": profile_id,
        "output_sha256": media_hash,
        "reviewer": "owner",
        "reviewed_at": "2026-09-25T12:00:00Z",
        "preview_context": "target app preview on a representative phone",
        "checks": checks,
        "note": "checked",
    }


class PlatformDeliveryTests(unittest.TestCase):
    def test_ffprobe_parser_normalizes_expected_metadata(self):
        metadata = MODULE.parse_ffprobe(probe())
        self.assertEqual(metadata["container"], "mp4")
        self.assertEqual(metadata["aspect_ratio"], "9:16")
        self.assertEqual(metadata["orientation"], "vertical")
        self.assertEqual(metadata["fps"], 30)
        self.assertEqual(metadata["audio_sample_rate_hz"], 48000)

    def test_technical_pass_is_not_delivery_ready_without_live_preview(self):
        result = MODULE.evaluate_delivery(profile(), MODULE.parse_ffprobe(probe()))
        self.assertEqual(result["technical_status"], "passed")
        self.assertEqual(result["manual_review_status"], "pending")
        self.assertEqual(result["delivery_status"], "needs_manual_preview")
        self.assertIn("LIVE_PREVIEW_REQUIRED", {item["code"] for item in result["findings"]})

    def test_hash_bound_review_makes_compliant_delivery_ready(self):
        digest = "d" * 64
        selected = profile()
        result = MODULE.evaluate_delivery(
            selected,
            MODULE.parse_ffprobe(probe()),
            review(selected["id"], digest),
            digest,
        )
        self.assertEqual(result["technical_status"], "passed")
        self.assertEqual(result["manual_review_status"], "passed")
        self.assertEqual(result["delivery_status"], "ready")

    def test_review_for_old_render_is_rejected(self):
        selected = profile()
        with self.assertRaisesRegex(MODULE.DeliveryCheckError, "does not match"):
            MODULE.evaluate_delivery(
                selected,
                MODULE.parse_ffprobe(probe()),
                review(selected["id"], "e" * 64),
                "f" * 64,
            )

    def test_failed_visual_check_blocks_delivery(self):
        digest = "d" * 64
        selected = profile()
        result = MODULE.evaluate_delivery(
            selected,
            MODULE.parse_ffprobe(probe()),
            review(selected["id"], digest, face_not_obscured=False),
            digest,
        )
        self.assertEqual(result["manual_review_status"], "failed")
        self.assertEqual(result["delivery_status"], "failed")
        self.assertIn("face_not_obscured", result["findings"][-1]["message"])

    def test_short_over_three_minutes_fails_official_eligibility(self):
        result = MODULE.evaluate_delivery(profile(), MODULE.parse_ffprobe(probe("181.0")))
        codes = {item["code"] for item in result["findings"]}
        self.assertIn("OFFICIAL_SHORTS_MAX_DURATION", codes)
        self.assertEqual(result["technical_status"], "failed")

    def test_horizontal_short_fails_official_eligibility(self):
        fixture = probe()
        fixture["streams"][0]["width"] = 1920
        fixture["streams"][0]["height"] = 1080
        result = MODULE.evaluate_delivery(profile(), MODULE.parse_ffprobe(fixture))
        codes = {item["code"] for item in result["findings"]}
        self.assertIn("OFFICIAL_SHORTS_ORIENTATION", codes)
        self.assertEqual(result["delivery_status"], "failed")

    def test_codec_resolution_color_and_audio_drift_fail_internal_contract(self):
        fixture = probe()
        video = fixture["streams"][0]
        audio = fixture["streams"][1]
        video.update({"width": 720, "height": 1280, "codec_name": "hevc", "color_space": "unknown"})
        audio.update({"codec_name": "mp3", "sample_rate": "44100"})
        result = MODULE.evaluate_delivery(profile(), MODULE.parse_ffprobe(fixture))
        codes = {item["code"] for item in result["findings"]}
        self.assertTrue(
            {
                "INTERNAL_WIDTH",
                "INTERNAL_HEIGHT",
                "INTERNAL_VIDEO_CODEC",
                "INTERNAL_COLOR_SPACE",
                "INTERNAL_AUDIO_CODEC",
                "INTERNAL_AUDIO_RATE",
            }.issubset(codes)
        )
        self.assertEqual(result["technical_status"], "failed")

    def test_missing_audio_stream_is_a_failure_not_a_crash(self):
        fixture = probe()
        fixture["streams"] = [fixture["streams"][0]]
        result = MODULE.evaluate_delivery(profile(), MODULE.parse_ffprobe(fixture))
        codes = {item["code"] for item in result["findings"]}
        self.assertIn("INTERNAL_AUDIO_CODEC", codes)
        self.assertIn("INTERNAL_AUDIO_RATE", codes)
        self.assertEqual(result["delivery_status"], "failed")

    def test_malformed_manual_review_fails_closed(self):
        selected = profile()
        malformed = review(selected["id"], "a" * 64)
        del malformed["checks"]["content_semantics_unchanged"]
        with self.assertRaisesRegex(MODULE.DeliveryCheckError, "review checks"):
            MODULE.evaluate_delivery(
                selected,
                MODULE.parse_ffprobe(probe()),
                malformed,
                "a" * 64,
            )

    def test_cli_status_transitions_from_preview_needed_to_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "delivery.mp4"
            media.write_bytes(b"encoded-fixture")
            probe_path = root / "probe.json"
            probe_path.write_text(json.dumps(probe()), encoding="utf-8")
            output = root / "check.json"
            args = [
                "--catalog",
                str(FRAMEWORK / "platforms/catalog.json"),
                "--profile",
                profile()["id"],
                "--media",
                str(media),
                "--probe-json",
                str(probe_path),
                "--out",
                str(output),
            ]
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                first_code = MODULE.main(args)
            self.assertEqual(first_code, 4)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["delivery_status"],
                "needs_manual_preview",
            )

            media_hash = hashlib.sha256(media.read_bytes()).hexdigest()
            review_path = root / "review.json"
            review_path.write_text(
                json.dumps(review(profile()["id"], media_hash)), encoding="utf-8"
            )
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                second_code = MODULE.main([*args, "--review", str(review_path)])
            self.assertEqual(second_code, 0)
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["delivery_status"], "ready"
            )


if __name__ == "__main__":
    unittest.main()
