#!/usr/bin/env python3

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import preflight_project as MODULE  # noqa: E402


class ProjectPreflightTests(unittest.TestCase):
    def test_audio_selection_accepts_audited_object(self):
        self.assertEqual(MODULE.selected_audio_index({"index": 2, "method": "comparative_listen"}), 2)
        self.assertEqual(MODULE.selected_audio_index("1"), 1)
        self.assertIsNone(MODULE.selected_audio_index("pending_listen"))

    def test_exact_rejected_copy_is_blocked_in_active_audio_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            active = project / "VIDEO-02/audio/sfx"
            active.mkdir(parents=True)
            rejected = active / "renamed.wav"
            rejected.write_bytes(b"rejected-audio-test")
            catalog = {
                "SFX-TEST-0001": {
                    "sha256": MODULE.sha256(rejected),
                    "status": "deprecated",
                    "approval": {"user_approval_status": "explicit_rejected"},
                    "reuse": {"policy": "do_not_reuse"},
                }
            }
            findings = []
            MODULE.scan_forbidden_file_copies(
                project, catalog, {"SFX-TEST-0001"}, [], findings
            )
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["code"], "FORBIDDEN_FILE_IN_ACTIVE_TREE")

    def test_requested_video_filter_ignores_other_video_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            active = project / "VIDEO-03/audio/sfx"
            active.mkdir(parents=True)
            rejected = active / "rejected.wav"
            rejected.write_bytes(b"rejected-audio-test")
            catalog = {"SFX-TEST-0001": {"sha256": MODULE.sha256(rejected)}}
            findings = []
            MODULE.scan_forbidden_file_copies(
                project, catalog, {"SFX-TEST-0001"}, ["VIDEO-02"], findings
            )
            self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
