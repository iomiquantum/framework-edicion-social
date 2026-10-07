#!/usr/bin/env python3

import json
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
FRAMEWORK = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import schema_validation as VALIDATOR  # noqa: E402


CONTRACTS = (
    ("creative-blueprint.schema.json", "creative-blueprint.json"),
    ("style-decision.schema.json", "style-decision.json"),
    ("variant-plan.schema.json", "variant-plan.json"),
    ("golden-master-registry.schema.json", "golden-master-registry.json"),
)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class CreativeContractTests(unittest.TestCase):
    def test_all_templates_validate_with_supported_schema_subset(self):
        for schema_name, template_name in CONTRACTS:
            with self.subTest(template=template_name):
                schema = load(FRAMEWORK / "schemas" / schema_name)
                template = load(FRAMEWORK / "templates" / template_name)
                VALIDATOR.assert_supported_schema(schema)
                self.assertEqual(VALIDATOR.validate_document(template, schema), [])

    def test_blueprint_requires_traceable_beats_and_rejects_unknown_fields(self):
        schema = load(FRAMEWORK / "schemas/creative-blueprint.schema.json")
        blueprint = load(FRAMEWORK / "templates/creative-blueprint.json")
        del blueprint["beats"][0]["trace_ids"]
        blueprint["unexpected"] = True
        errors = VALIDATOR.validate_document(blueprint, schema)
        self.assertTrue(any("trace_ids" in error for error in errors))
        self.assertTrue(any("unexpected property" in error for error in errors))

    def test_variant_template_locks_every_shared_body_layer(self):
        plan = load(FRAMEWORK / "templates/variant-plan.json")
        lock_fields = (
            "edit_points_locked",
            "voice_locked",
            "caption_timing_locked",
            "semantic_plan_locked",
            "approved_assets_locked",
            "face_safe_zones_locked",
        )
        self.assertTrue(all(plan["shared_body"][field] is True for field in lock_fields))
        self.assertGreaterEqual(len(plan["variants"]), 2)
        self.assertTrue(all(item["body_reference"] == "shared_body" for item in plan["variants"]))


if __name__ == "__main__":
    unittest.main()
