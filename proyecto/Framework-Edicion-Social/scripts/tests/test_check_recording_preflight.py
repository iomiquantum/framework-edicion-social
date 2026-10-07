#!/usr/bin/env python3

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "check_recording_preflight.py"
SPEC = importlib.util.spec_from_file_location("check_recording_preflight", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
TEMPLATE = Path(__file__).resolve().parents[2] / "templates/recording-preflight.json"


def valid_probe(include_audio=True):
    streams = [
        {
            "codec_type": "video",
            "codec_name": "h264",
            "width": 1280,
            "height": 720,
            "avg_frame_rate": "30000/1001",
            "r_frame_rate": "30/1",
            "color_space": "bt709",
            "color_transfer": "bt709",
            "color_primaries": "bt709",
            "side_data_list": [{"rotation": -90}],
        }
    ]
    if include_audio:
        streams.append(
            {
                "codec_type": "audio",
                "codec_name": "aac",
                "sample_rate": "48000",
                "channels": 2,
                "channel_layout": "stereo",
            }
        )
    return {"streams": streams, "format": {"format_name": "mov,mp4", "duration": "12.5", "size": "1000"}}


class RecordingPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_rotation_is_applied_before_resolution_and_orientation_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "recording.mp4"
            source.write_bytes(b"probe-is-injected")
            report = MODULE.run_preflight(source, self.config, probe_runner=lambda *_args, **_kwargs: valid_probe())
            self.assertEqual(report["probe"]["video"]["display_width"], 720)
            self.assertEqual(report["probe"]["video"]["display_height"], 1280)
            self.assertEqual(report["probe"]["video"]["orientation"], "portrait")
            self.assertEqual(report["summary"]["status"], "pass")

    def test_required_audio_missing_is_a_hard_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "recording.mp4"
            source.write_bytes(b"probe-is-injected")
            report = MODULE.run_preflight(source, self.config, probe_runner=lambda *_args, **_kwargs: valid_probe(False))
            audio_check = next(item for item in report["checks"] if item["id"] == "PF-005")
            self.assertEqual(audio_check["status"], "fail")
            self.assertFalse(report["summary"]["delivery_ready"])

    def test_probe_failure_is_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "recording.mp4"
            source.write_bytes(b"not-media")

            def fail(*_args, **_kwargs):
                raise MODULE.PreflightError("simulated ffprobe failure")

            report = MODULE.run_preflight(source, self.config, probe_runner=fail)
            self.assertIsNone(report["probe"])
            self.assertEqual(report["summary"]["status"], "fail")
            self.assertIn("simulated", report["checks"][1]["message"])

    def test_missing_source_and_invalid_policy_fail_safely(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "missing.mp4"
            report = MODULE.run_preflight(source, self.config)
            self.assertEqual(report["checks"][0]["status"], "fail")
            self.assertEqual(report["checks"][1]["status"], "not_run")
        invalid = copy.deepcopy(self.config)
        invalid["policy"]["max_fps"] = 10
        with self.assertRaisesRegex(MODULE.PreflightError, "fps range"):
            MODULE.validate_config(invalid)


if __name__ == "__main__":
    unittest.main()
