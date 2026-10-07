#!/usr/bin/env python3

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "build_take_proxies.py"


def file_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class BuildTakeProxiesIntegrationTests(unittest.TestCase):
    def test_proxy_is_verified_and_linked_to_original(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            project.mkdir()
            source = root / "source.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", "color=c=blue:s=640x360:r=30:d=2",
                    "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=2",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(source),
                ],
                check=True,
            )
            take_map_path = root / "take-map-test.json"
            take_map = {
                "schema_version": "1.0.0",
                "project_id": "test",
                "source": {
                    "id": "SOURCE-TEST",
                    "path": str(source),
                    "sha256": file_hash(source),
                    "fps": 30,
                    "audio_stream_index": 1,
                },
                "transcript": {},
                "marker_protocol": "compact_v1",
                "videos": [
                    {
                        "video_id": "VIDEO-01",
                        "selected_take_id": "VIDEO-01-TAKE-01",
                        "takes": [
                            {
                                "take_id": "VIDEO-01-TAKE-01",
                                "video_id": "VIDEO-01",
                                "candidate_range": {"start_s": 0.2, "end_s": 1.2},
                                "decision": {"status": "approved"},
                            }
                        ],
                    }
                ],
                "qa": {"human_review_completed": True},
            }
            take_map_path.write_text(json.dumps(take_map), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable, str(SCRIPT), "--take-map", str(take_map_path),
                    "--project", str(project), "--max-dimension", "480",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("proxy:", completed.stdout)
            proxy = project / "VIDEO-01/source/video-01-take-01-proxy.mp4"
            source_range = project / "VIDEO-01/source/video-01-take-01-source-range.json"
            self.assertTrue(proxy.is_file())
            self.assertTrue(source_range.is_file())
            metadata = json.loads(source_range.read_text(encoding="utf-8"))
            self.assertEqual(metadata["verification_status"], "pass")
            self.assertEqual(metadata["proxy_sha256"], file_hash(proxy))
            self.assertTrue(metadata["final_render_must_use_original"])
            self.assertAlmostEqual(metadata["duration_s"], 1.0, places=5)
            self.assertAlmostEqual(metadata["proxy_duration_s"], 1.0, delta=0.25)


if __name__ == "__main__":
    unittest.main()
