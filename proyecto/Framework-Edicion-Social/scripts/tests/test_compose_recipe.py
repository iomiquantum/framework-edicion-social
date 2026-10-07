#!/usr/bin/env python3

import copy
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
FRAMEWORK = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import compose_recipe as MODULE  # noqa: E402
import schema_validation as VALIDATOR  # noqa: E402


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def template(name):
    return load(FRAMEWORK / "templates" / f"{name}.json")


def catalog():
    return load(FRAMEWORK / "creative-recipes" / "catalog.json")


def one_per_kind(source, module_ids):
    result = copy.deepcopy(source)
    result["modules"] = [
        copy.deepcopy(module)
        for module in source["modules"]
        if module["id"] in set(module_ids)
    ]
    allowed = {module["id"] for module in result["modules"]}
    for module in result["modules"]:
        module["requires_any_modules"] = [
            value for value in module["requires_any_modules"] if value in allowed
        ]
        module["incompatible_with"] = [
            value for value in module["incompatible_with"] if value in allowed
        ]
    return result


def governed_asset_index(*specifications):
    index = template("asset-index")
    assets = []
    for position, specification in enumerate(specifications, start=1):
        asset_id = specification["asset_id"]
        asset_type = specification["type"]
        assets.append(
            {
                "asset_id": asset_id,
                "source_asset_ids": [asset_id],
                "name": asset_id,
                "type": asset_type,
                "format": "wav" if asset_type in {"sfx", "bgm"} else "png",
                "sha256": f"{position:064x}",
                "bytes": 100 + position,
                "status": specification.get("status", "approved"),
                "description": f"Governed test asset {asset_id}",
                "semantic_tags": specification.get("semantic_tags", []),
                "intent_phrases": specification.get("intent_phrases", []),
                "avoid_for": [],
                "locations": [f"assets/{asset_id.lower()}.bin"],
                "metadata": {
                    "technical": specification.get("technical", {}),
                    "approval": {},
                },
                "provenance_records": [
                    {
                        "source_kind": "explicit_folder",
                        "source_ref": "assets",
                        "source_asset_id": asset_id,
                        "path": f"assets/{asset_id.lower()}.bin",
                        "details": specification.get("provenance_details", {}),
                    }
                ],
                "reuse": {
                    "policy": specification.get("reuse_policy", "unlimited"),
                    "cooldown_videos": 0,
                    "cooldown_enforcement": "advisory_non_blocking",
                },
                "usage": {
                    "usage_count": 0,
                    "used_in": [],
                    "last_used_at": None,
                    "last_used_sequence": None,
                    "events": [],
                },
            }
        )
    index["assets"] = assets
    index["summary"]["asset_count"] = len(assets)
    index["summary"]["source_record_count"] = len(assets)
    index["summary"]["status_counts"] = {}
    index["summary"]["type_counts"] = {}
    for asset in assets:
        index["summary"]["status_counts"][asset["status"]] = (
            index["summary"]["status_counts"].get(asset["status"], 0) + 1
        )
        index["summary"]["type_counts"][asset["type"]] = (
            index["summary"]["type_counts"].get(asset["type"], 0) + 1
        )
    return index


def series_memory_with(module_ids, count=3):
    memory = template("series-variety-ledger")
    memory["entries"] = [
        {
            "video_id": f"VIDEO-{index:02d}",
            "fingerprint_id": f"FP-VIDEO-{index:02d}-{index:012X}",
            "fingerprint_path": f"fingerprints/VIDEO-{index:02d}.json",
            "fingerprint_sha256": f"{index:064x}",
            "family_id": None,
            "archetype_id": None,
            "approval_status": "unreviewed",
            "approval_ref": None,
            "approved_artifact_sha256": None,
            "approved_at": None,
            "technical_qa": {
                "status": "unavailable",
                "evidence_path": None,
                "evidence_sha256": None,
                "artifact_sha256": None,
            },
            "recorded_at": f"2026-09-{20 + index:02d}",
            "fields": {"recipe_module_ids": list(module_ids.values())},
            "traits": {},
        }
        for index in range(1, count + 1)
    ]
    return memory


class CreativeRecipeCompilerTests(unittest.TestCase):
    def setUp(self):
        self.blueprint = template("creative-blueprint")
        self.catalog = catalog()

    def test_catalog_and_repository_plan_templates_validate(self):
        catalog_schema = load(FRAMEWORK / "schemas/creative-recipe-catalog.schema.json")
        plan_schema = load(FRAMEWORK / "schemas/creative-recipe-plan.schema.json")
        plan_template = template("creative-recipe-plan")
        for schema in (catalog_schema, plan_schema):
            VALIDATOR.assert_supported_schema(schema)
        self.assertEqual(VALIDATOR.validate_document(self.catalog, catalog_schema), [])
        self.assertEqual(VALIDATOR.validate_document(plan_template, plan_schema), [])
        MODULE.validate_catalog(self.catalog)
        MODULE.validate_plan(plan_template, catalog=self.catalog)

    def test_compilation_is_deterministic_varied_and_never_auto_selects(self):
        first = MODULE.build_plan(self.blueprint, self.catalog)
        second = MODULE.build_plan(self.blueprint, self.catalog)
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "proposed")
        self.assertGreaterEqual(first["proposal_count"], 2)
        self.assertLessEqual(first["proposal_count"], 3)
        policy = first["recommendation_policy"]
        self.assertFalse(policy["single_global_winner"])
        self.assertFalse(policy["automatic_promotion"])
        self.assertTrue(policy["human_choice_required"])
        self.assertEqual(
            policy["ranking_meaning"],
            "contextual_review_order_not_quality_or_universal_winner",
        )
        first_modules = first["proposals"][0]["module_ids"]
        for proposal in first["proposals"]:
            self.assertEqual(set(proposal["module_ids"]), set(MODULE.KINDS))
            self.assertEqual(len(proposal["score_breakdown"]), 6)
            self.assertTrue(proposal["compatibility"]["passed"])
            self.assertEqual(proposal["compatibility"]["blocking_conflicts"], [])
            self.assertFalse(proposal["fatigue"]["is_quality_score"])
            self.assertTrue(proposal["variety"]["not_quality_score"])
            contributors = proposal["contributing_family_ids"]
            self.assertEqual(contributors, sorted(set(contributors)))
            self.assertEqual(proposal["hybrid"], len(contributors) > 1)
            if contributors:
                self.assertIn(proposal["primary_family_id"], contributors)
            else:
                self.assertIsNone(proposal["primary_family_id"])
        for proposal in first["proposals"][1:]:
            changed = {
                kind
                for kind in MODULE.KINDS
                if proposal["module_ids"][kind] != first_modules[kind]
            }
            self.assertGreaterEqual(len(changed), 2)
            self.assertTrue(changed & {"structure", "visual_system", "motion"})

    def test_catalog_requirements_and_incompatibilities_are_enforced(self):
        selected_ids = {
            "HOOK-CONTRARIAN-OUTCOME",
            "STRUCT-CLAIM-PROOF-ACTION",
            "VIS-FULLSCREEN-CONCEPT-CUTAWAY",
            "MOTION-WHIP-MATCHED-CUTAWAYS",
            "SOUND-VOICE-FIRST-MINIMAL",
            "CTA-REFLECTIVE-QUESTION",
        }
        incompatible = one_per_kind(self.catalog, selected_ids)
        whip = next(
            module for module in incompatible["modules"]
            if module["id"] == "MOTION-WHIP-MATCHED-CUTAWAYS"
        )
        whip["requires_any_modules"] = ["VIS-FULLSCREEN-CONCEPT-CUTAWAY"]
        plan = MODULE.build_plan(self.blueprint, incompatible)
        self.assertEqual(plan["status"], "abstained")
        self.assertIn("no_compatible_combinations", plan["abstention_reasons"])

    def test_sparse_blueprint_context_produces_valid_abstention(self):
        sparse = copy.deepcopy(self.blueprint)
        for values in sparse["style_selection_signals"].values():
            values.clear()
        plan = MODULE.build_plan(sparse, self.catalog)
        self.assertEqual(plan["status"], "abstained")
        self.assertEqual(plan["proposal_count"], 0)
        self.assertEqual(plan["proposals"], [])
        self.assertIn("insufficient_blueprint_signals", plan["abstention_reasons"])

    def test_recent_repetition_is_a_warning_and_penalty_not_quality_or_block(self):
        top = MODULE.build_plan(self.blueprint, self.catalog, count=1)["proposals"][0]
        restricted = one_per_kind(self.catalog, set(top["module_ids"].values()))
        memory = series_memory_with(top["module_ids"])
        plan = MODULE.build_plan(
            self.blueprint,
            restricted,
            series_memory=memory,
            series_memory_path="memory.json",
            count=1,
        )
        self.assertEqual(plan["status"], "proposed")
        fatigue = plan["proposals"][0]["fatigue"]
        self.assertEqual(fatigue["signal"], "warning")
        self.assertGreater(fatigue["penalty"], 0)
        self.assertFalse(fatigue["is_quality_score"])
        self.assertIn("creative_fatigue:warning", plan["proposals"][0]["compatibility"]["warnings"])

    def test_asset_index_reports_coverage_and_real_gaps(self):
        top = MODULE.build_plan(self.blueprint, self.catalog, count=1)["proposals"][0]
        restricted = one_per_kind(self.catalog, set(top["module_ids"].values()))
        covered = governed_asset_index(
            {"asset_id": "IMG-1", "type": "image"},
            {"asset_id": "SFX-1", "type": "sfx"},
            {
                "asset_id": "ICON-1",
                "type": "icon",
                "semantic_tags": ["diagrama", "tipografía"],
            },
        )
        covered_plan = MODULE.build_plan(
            self.blueprint,
            restricted,
            asset_index=covered,
            asset_index_path="asset-index.json",
            count=1,
        )
        self.assertTrue(covered_plan["proposals"][0]["asset_fit"]["index_provided"])
        self.assertEqual(covered_plan["proposals"][0]["asset_fit"]["coverage_status"], "covered")
        self.assertIn("diagram", MODULE._asset_types_from_index(covered))
        self.assertIn("typographic_overlay", MODULE._asset_types_from_index(covered))

        gaps_plan = MODULE.build_plan(
            self.blueprint,
            restricted,
            asset_index=governed_asset_index(),
            asset_index_path="empty-assets.json",
            count=1,
        )
        asset_fit = gaps_plan["proposals"][0]["asset_fit"]
        self.assertEqual(asset_fit["coverage_status"], "gaps")
        self.assertIn("sfx", asset_fit["missing_types"])
        self.assertGreaterEqual(gaps_plan["proposals"][0]["effort"]["asset_generation_count"], 1)

    def test_optional_inputs_reject_partial_documents_and_ignore_ineligible_asset_types(self):
        with self.assertRaisesRegex(MODULE.CreativeRecipeError, "Series variety ledger"):
            MODULE.build_plan(
                self.blueprint,
                self.catalog,
                series_memory={"policy": {"comparison_window": 3}, "entries": []},
            )
        with self.assertRaisesRegex(MODULE.CreativeRecipeError, "Semantic asset index"):
            MODULE.build_plan(self.blueprint, self.catalog, asset_index={"assets": []})

        index = governed_asset_index(
            {
                "asset_id": "IMG-META-SFX",
                "type": "image",
                "technical": {"type": "sfx"},
                "provenance_details": {"kind": "sfx"},
            },
            {
                "asset_id": "SFX-NO-REUSE",
                "type": "sfx",
                "reuse_policy": "do_not_reuse",
            },
        )
        self.assertEqual(MODULE._asset_types_from_index(index), {"image"})

    def test_family_attribution_has_one_primary_and_marks_hybrids(self):
        plan = MODULE.build_plan(self.blueprint, self.catalog, count=3)
        hybrid = next(proposal for proposal in plan["proposals"] if proposal["hybrid"])
        self.assertGreater(len(hybrid["contributing_family_ids"]), 1)
        self.assertIn(hybrid["primary_family_id"], hybrid["contributing_family_ids"])

        tampered = copy.deepcopy(plan)
        tampered["proposals"][0]["primary_family_id"] = "FAMILY-NOT-A-CONTRIBUTOR"
        with self.assertRaisesRegex(MODULE.CreativeRecipeError, "Primary family"):
            MODULE.validate_plan(tampered, catalog=self.catalog)

    def test_optional_series_contract_is_traceable_without_global_winner(self):
        contract = template("series-contract")
        plan = MODULE.build_plan(
            self.blueprint,
            self.catalog,
            series_contract=contract,
            series_contract_path="series-contract.json",
            count=1,
        )
        self.assertIsNotNone(plan["inputs"]["series_contract"]["sha256"])
        self.assertTrue(plan["recommendation_policy"]["preserve_multiple_families"])
        self.assertFalse(plan["recommendation_policy"]["single_global_winner"])

    def test_paths_are_confined_and_cli_never_overwrites_an_input(self):
        with self.assertRaisesRegex(MODULE.CreativeRecipeError, "outside the workspace"):
            MODULE._confined_path("/private/tmp/creative-recipe-outside.json", must_exist=False)

        with tempfile.TemporaryDirectory(prefix="recipe-cli-", dir=FRAMEWORK) as temporary:
            root = Path(temporary)
            blueprint_path = root / "blueprint.json"
            catalog_path = root / "catalog.json"
            output_path = root / "plan.json"
            blueprint_path.write_text(json.dumps(self.blueprint), encoding="utf-8")
            catalog_path.write_text(json.dumps(self.catalog), encoding="utf-8")
            self.assertEqual(
                MODULE.main([
                    "--blueprint", str(blueprint_path),
                    "--catalog", str(catalog_path),
                    "--out", str(output_path),
                    "--count", "2",
                ]),
                0,
            )
            MODULE.validate_plan(load(output_path), catalog=self.catalog)
            stderr = StringIO()
            with redirect_stderr(stderr):
                code = MODULE.main([
                    "--blueprint", str(blueprint_path),
                    "--catalog", str(catalog_path),
                    "--out", str(blueprint_path),
                ])
            self.assertEqual(code, 2)
            self.assertIn("may not overwrite an input", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
