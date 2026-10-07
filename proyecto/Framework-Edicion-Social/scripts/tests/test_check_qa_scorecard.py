#!/usr/bin/env python3

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
SCRIPT = SCRIPTS / "check_qa_scorecard.py"
TEMPLATE = SCRIPTS.parent / "templates/qa-scorecard.json"
SPEC = importlib.util.spec_from_file_location("check_qa_scorecard", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def load_template():
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def all_checks(scorecard):
    for section in scorecard["sections"].values():
        yield from section["hard_gates"]
        yield from section["editorial_criteria"]


def ready_scorecard():
    scorecard = load_template()
    scorecard.update(
        {
            "scorecard_id": "QA-TEST-001",
            "project_id": "PROJECT-TEST",
            "video_id": "VIDEO-01",
            "render_id": "RENDER-001",
            "evaluated_at": "2026-09-25T12:00:00Z",
        }
    )
    digest = "a" * 64
    scorecard["artifacts"].update(
        {
            "source_manifest_path": "source/manifest.json",
            "source_sha256": digest,
            "approved_take_id": "VIDEO-01-TAKE-01",
            "transcript_path": "transcript.json",
            "transcript_sha256": digest,
            "cut_plan_path": "cut-plan.json",
            "cut_plan_sha256": digest,
            "render_path": "render.mp4",
            "render_sha256": digest,
            "render_manifest_path": "render-manifest.json",
            "framework_version": "1.3.0",
            "hyperframes_version": "test",
        }
    )
    for index, check in enumerate(all_checks(scorecard), 1):
        check["status"] = "pass"
        if check["id"].startswith("HG-") and check["verification_mode"] == "automatic":
            check["evidence"] = [
                {
                    "evidence_id": f"EVID-TEST-{index:03d}",
                    "kind": "metric",
                    "artifact_sha256": digest,
                    "metric": "automated_gate_result",
                    "value": True,
                    "unit": "boolean",
                    "note": "Machine result for the exact final render hash.",
                }
            ]
        else:
            check["evidence"] = [
                {
                    "evidence_id": f"EVID-TEST-{index:03d}",
                    "kind": "visual_observation",
                    "observed_by": "qa-test",
                    "note": "Verified against the final render timeline.",
                }
            ]
    scorecard["editorial_signoff"].update(
        {"status": "pass", "reviewer": "qa-test", "reviewed_at": "2026-09-25T12:05:00Z"}
    )
    scorecard["summary"].update(
        {
            "hard_gate_counts": {"total": 26, "pass": 26, "warn": 0, "fail": 0, "not_run": 0},
            "editorial_counts": {"total": 16, "pass": 16, "warn": 0, "fail": 0, "not_run": 0},
            "hard_gate_status": "pass",
            "editorial_status": "pass",
            "delivery_decision": "ready",
            "delivery_allowed": True,
            "blocking_check_ids": [],
            "warning_check_ids": [],
            "unresolved_exception_ids": [],
        }
    )
    return scorecard


class QAScorecardTests(unittest.TestCase):
    def test_blank_template_is_valid_but_delivery_is_blocked(self):
        scorecard = load_template()
        self.assertTrue(MODULE.is_initial_template(scorecard))
        report = MODULE.analyze_scorecard(scorecard, template_mode=True)
        self.assertTrue(report["valid"])
        self.assertFalse(report["delivery_ready"])
        self.assertIn("HG-SRC-001", report["blockers"])

    def test_fully_evidenced_scorecard_can_be_ready(self):
        report = MODULE.analyze_scorecard(ready_scorecard())
        self.assertTrue(report["valid"], report["errors"])
        self.assertTrue(report["delivery_ready"])

    def test_missing_evidence_invalidates_an_evaluated_check(self):
        scorecard = ready_scorecard()
        scorecard["sections"]["source_and_take"]["hard_gates"][0]["evidence"] = []
        report = MODULE.analyze_scorecard(scorecard)
        self.assertFalse(report["valid"])
        self.assertIn("CHECK_EVIDENCE_MISSING", {item["code"] for item in report["errors"]})
        self.assertFalse(report["delivery_ready"])

    def test_required_hard_not_run_blocks_delivery(self):
        scorecard = ready_scorecard()
        check = scorecard["sections"]["source_and_take"]["hard_gates"][0]
        check["status"] = "not_run"
        check["evidence"] = []
        scorecard["summary"].update(
            {
                "hard_gate_counts": {"total": 26, "pass": 25, "warn": 0, "fail": 0, "not_run": 1},
                "hard_gate_status": "not_run",
                "delivery_decision": "pending",
                "delivery_allowed": False,
                "blocking_check_ids": [check["id"]],
            }
        )
        report = MODULE.analyze_scorecard(scorecard)
        self.assertTrue(report["valid"], report["errors"])
        self.assertFalse(report["delivery_ready"])
        self.assertIn(check["id"], report["blockers"])

    def test_accepted_exception_never_overrides_a_hard_fail(self):
        scorecard = ready_scorecard()
        check = scorecard["sections"]["source_and_take"]["hard_gates"][0]
        check.update({"status": "fail", "notes": "Source hash mismatch.", "exception_ids": ["EXC-TEST-001"]})
        scorecard["exceptions"] = [
            {
                "id": "EXC-TEST-001",
                "check_ids": [check["id"]],
                "start_s": None,
                "end_s": None,
                "reason": "Delivery requested despite mismatch.",
                "risk": "The wrong source could be delivered.",
                "compensating_controls": ["Manual source comparison completed."],
                "requested_by": "producer",
                "approved_by": "editor",
                "approved_at": "2026-09-25T12:04:00Z",
                "disposition": "accepted",
                "hard_gate_override": False,
            }
        ]
        scorecard["editorial_signoff"]["accepted_exception_ids"] = ["EXC-TEST-001"]
        scorecard["summary"].update(
            {
                "hard_gate_counts": {"total": 26, "pass": 25, "warn": 0, "fail": 1, "not_run": 0},
                "hard_gate_status": "fail",
                "delivery_decision": "blocked",
                "delivery_allowed": False,
                "blocking_check_ids": [check["id"]],
            }
        )
        report = MODULE.analyze_scorecard(scorecard)
        self.assertTrue(report["valid"], report["errors"])
        self.assertFalse(report["delivery_ready"])
        self.assertIn(check["id"], report["blockers"])

    def test_malformed_lists_are_rejected_without_crashing(self):
        scorecard = ready_scorecard()
        scorecard["summary"]["warning_check_ids"] = None
        scorecard["exceptions"] = [{"id": "EXC-BROKEN", "check_ids": {"bad": True}}]
        malformed_check = scorecard["sections"]["source_and_take"]["hard_gates"][0]
        malformed_check["id"] = ["not", "hashable"]
        malformed_check["status"] = {"also": "not hashable"}
        scorecard["editorial_signoff"]["status"] = {"bad": True}
        scorecard["summary"]["delivery_decision"] = {"bad": True}
        report = MODULE.analyze_scorecard(scorecard)
        self.assertFalse(report["valid"])
        self.assertTrue(report["errors"])

    def test_python_boolean_number_equivalence_does_not_bypass_types(self):
        scorecard = ready_scorecard()
        scorecard["policy"]["any_hard_fail_blocks_delivery"] = 1
        scorecard["summary"]["hard_gate_counts"]["fail"] = False
        scorecard["sections"]["source_and_take"]["hard_gates"][0]["evidence"][0]["device"] = {}
        report = MODULE.analyze_scorecard(scorecard)
        codes = {item["code"] for item in report["errors"]}
        self.assertFalse(report["valid"])
        self.assertIn("POLICY_DRIFT", codes)
        self.assertIn("COUNT_VALUE", codes)
        self.assertIn("EVIDENCE_DEVICE", codes)

    def test_optional_not_run_requires_explanation_outside_template(self):
        scorecard = ready_scorecard()
        check = scorecard["sections"]["source_and_take"]["editorial_criteria"][0]
        self.assertFalse(check["required"])
        check.update({"status": "not_run", "evidence": [], "notes": ""})
        scorecard["summary"].update(
            {
                "editorial_counts": {"total": 16, "pass": 15, "warn": 0, "fail": 0, "not_run": 1},
                "editorial_status": "pass",
            }
        )
        report = MODULE.analyze_scorecard(scorecard)
        self.assertIn("CHECK_NOT_APPLICABLE_NOTE", {item["code"] for item in report["errors"]})
        self.assertFalse(report["delivery_ready"])

    def test_automatic_gate_rejects_observation_only_evidence(self):
        scorecard = ready_scorecard()
        check = scorecard["sections"]["source_and_take"]["hard_gates"][0]
        self.assertEqual(check["verification_mode"], "automatic")
        check["evidence"] = [
            {
                "evidence_id": "EVID-OBSERVATION-ONLY",
                "kind": "visual_observation",
                "observed_by": "qa-test",
                "note": "Observation alone is not reproducible.",
            }
        ]
        report = MODULE.analyze_scorecard(scorecard)
        self.assertIn("AUTOMATIC_EVIDENCE", {item["code"] for item in report["errors"]})
        self.assertFalse(report["delivery_ready"])

    def test_schema_reference_and_version_are_pinned(self):
        for field, value, code in (
            ("$schema", "not-the-qa-schema", "SCHEMA_URI"),
            ("schema_version", "99.99.99", "SCHEMA_VERSION"),
        ):
            with self.subTest(field=field):
                scorecard = ready_scorecard()
                scorecard[field] = value
                report = MODULE.analyze_scorecard(scorecard)
                self.assertIn(code, {item["code"] for item in report["errors"]})

    def test_validate_only_cannot_bypass_hard_fail(self):
        scorecard = ready_scorecard()
        check = scorecard["sections"]["source_and_take"]["hard_gates"][0]
        check.update({"status": "fail", "notes": "Automated comparison failed."})
        scorecard["summary"].update(
            {
                "hard_gate_counts": {"total": 26, "pass": 25, "warn": 0, "fail": 1, "not_run": 0},
                "hard_gate_status": "fail",
                "delivery_decision": "blocked",
                "delivery_allowed": False,
                "blocking_check_ids": [check["id"]],
            }
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "hard-fail.json"
            path.write_text(json.dumps(scorecard), encoding="utf-8")
            gated = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True,
                text=True,
            )
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), str(path), "--validate-only"],
                capture_output=True,
                text=True,
            )
        self.assertEqual(gated.returncode, 1)
        self.assertIn("QA BLOCKED", gated.stdout)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("VALIDATE_ONLY_SCOPE", completed.stdout)


if __name__ == "__main__":
    unittest.main()
