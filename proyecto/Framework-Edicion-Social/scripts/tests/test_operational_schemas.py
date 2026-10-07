#!/usr/bin/env python3

import copy
import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/schema_validation.py"
SPEC = importlib.util.spec_from_file_location("schema_validation_operational", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class OperationalSchemaTests(unittest.TestCase):
    def validate_pair(self, name):
        template = json.loads((ROOT / f"templates/{name}.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / f"schemas/{name}.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(VALIDATOR.validate_document(template, schema), [])
        return template, schema

    def test_new_templates_match_supported_schemas(self):
        for name in (
            "production-board", "dependency-map", "recording-preflight",
            "performance-review", "creative-attribution",
        ):
            with self.subTest(name=name):
                self.validate_pair(name)

    def test_performance_review_cannot_promote_rules(self):
        template, schema = self.validate_pair("performance-review")
        mutated = copy.deepcopy(template)
        mutated["governance"]["automatic_rule_promotion"] = True
        errors = VALIDATOR.validate_document(mutated, schema)
        self.assertTrue(any("required constant False" in error for error in errors))

        mutated = copy.deepcopy(template)
        mutated["promoted_rule"] = "RULE-UNSAFE"
        errors = VALIDATOR.validate_document(mutated, schema)
        self.assertTrue(any("unexpected property" in error for error in errors))

        for confidence in ("high", "stronger_non_causal"):
            mutated = copy.deepcopy(template)
            mutated["interpretation"]["confidence"] = confidence
            errors = VALIDATOR.validate_document(mutated, schema)
            self.assertTrue(errors, confidence)

        for decision in ("retire_variant", "promote", "candidate_pattern"):
            mutated = copy.deepcopy(template)
            mutated["next_step"]["decision"] = decision
            errors = VALIDATOR.validate_document(mutated, schema)
            self.assertTrue(errors, decision)

        mutated = copy.deepcopy(template)
        mutated["evidence_status"] = {
            "status": "verified",
            "report_path": "reports/report.json",
            "report_sha256": "a" * 64,
            "cohort_id": "COHORT-0000000000000000",
            "metrics_evidence_sha256": "b" * 64,
            "notice": "claimed verified without a semantic verifier",
        }
        errors = VALIDATOR.validate_document(mutated, schema)
        self.assertTrue(errors)

    def test_production_board_schema_rejects_malformed_video_id(self):
        template, schema = self.validate_pair("production-board")
        mutated = copy.deepcopy(template)
        mutated["claims"] = [
            {
                "video_id": "video-one",
                "owner": "agent",
                "workload": "light",
                "claimed_at": "2026-09-25T00:00:00Z",
                "note": "",
            }
        ]
        errors = VALIDATOR.validate_document(mutated, schema)
        self.assertTrue(any("does not match" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
