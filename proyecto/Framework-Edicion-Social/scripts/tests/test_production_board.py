#!/usr/bin/env python3

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "production_board.py"
SPEC = importlib.util.spec_from_file_location("production_board", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ProductionBoardTests(unittest.TestCase):
    def test_single_owner_collision_and_owner_checked_release(self):
        with tempfile.TemporaryDirectory() as temporary:
            board = Path(temporary) / "board.json"
            MODULE.initialize(board, "PROJECT-1", 2)
            MODULE.claim_video(board, "VIDEO-01", "agent-a", "light")
            with self.assertRaises(MODULE.BoardConflict):
                MODULE.claim_video(board, "VIDEO-01", "agent-b", "light")
            with self.assertRaises(MODULE.BoardConflict):
                MODULE.release_video(board, "VIDEO-01", "agent-b")
            MODULE.release_video(board, "VIDEO-01", "agent-a")
            self.assertEqual(MODULE.board_status(board)["claims"], [])

    def test_heavy_capacity_and_idempotent_claim(self):
        with tempfile.TemporaryDirectory() as temporary:
            board = Path(temporary) / "board.json"
            MODULE.initialize(board, "PROJECT-1", 1)
            first, created = MODULE.claim_video(board, "VIDEO-01", "agent-a", "heavy")
            self.assertTrue(created)
            repeated, created = MODULE.claim_video(board, "VIDEO-01", "agent-a", "heavy")
            self.assertFalse(created)
            self.assertEqual(first["generation"], repeated["generation"])
            with self.assertRaises(MODULE.BoardConflict):
                MODULE.claim_video(board, "VIDEO-02", "agent-b", "heavy")
            _, light_created = MODULE.claim_video(board, "VIDEO-02", "agent-b", "light")
            self.assertTrue(light_created)

    def test_parallel_cli_claim_has_exactly_one_winner(self):
        with tempfile.TemporaryDirectory() as temporary:
            board = Path(temporary) / "board.json"
            MODULE.initialize(board, "PROJECT-1", 2)
            processes = [
                subprocess.Popen(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "--board",
                        str(board),
                        "claim",
                        "--video",
                        "VIDEO-09",
                        "--owner",
                        f"agent-{index}",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for index in range(4)
            ]
            results = [process.communicate(timeout=10) + (process.returncode,) for process in processes]
            self.assertEqual(sum(code == 0 for _, _, code in results), 1)
            self.assertEqual(sum(code == 3 for _, _, code in results), 3)
            self.assertEqual(len(MODULE.board_status(board)["claims"]), 1)

    def test_atomic_write_failure_keeps_original(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "board.json"
            original = {"sentinel": True}
            path.write_text(json.dumps(original), encoding="utf-8")
            with mock.patch.object(MODULE.os, "replace", side_effect=OSError("simulated")):
                with self.assertRaises(OSError):
                    MODULE.atomic_write_json(path, {"sentinel": False})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)
            self.assertEqual(list(path.parent.glob(f".{path.name}.*.tmp")), [])

    def test_duplicate_claims_in_malformed_board_are_rejected(self):
        claim = {
            "video_id": "VIDEO-01",
            "owner": "agent-a",
            "workload": "light",
            "claimed_at": "2026-09-25T00:00:00+00:00",
            "note": "",
        }
        board = {
            "schema_version": "1.0.0",
            "project_id": "P",
            "max_heavy_jobs": 1,
            "generation": 0,
            "claims": [claim, dict(claim)],
            "updated_at": "",
        }
        with self.assertRaisesRegex(MODULE.BoardError, "duplicate"):
            MODULE.validate_board(board)


if __name__ == "__main__":
    unittest.main()
