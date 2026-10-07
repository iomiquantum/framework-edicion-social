#!/usr/bin/env python3

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
SCRIPT = SCRIPTS / "validate_framework.py"
SPEC = importlib.util.spec_from_file_location("validate_framework", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FrameworkStyleValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(MODULE.STYLE_CATALOG.read_text(encoding="utf-8"))
        cls.style_schema = MODULE.load("schemas/style.schema.json")
        cls.motion_schema = MODULE.load("schemas/motion-style.schema.json")

    def test_declared_style_hashes_match_portable_packages(self):
        self.assertEqual(
            MODULE.validate_styles(self.catalog, self.style_schema, self.motion_schema),
            len(self.catalog["styles"]),
        )

    def test_style_hash_drift_is_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["styles"][0]["package_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "hash drift"):
            MODULE.validate_styles(catalog, self.style_schema, self.motion_schema)

    def test_canonical_path_traversal_and_absolute_paths_are_rejected(self):
        style_id = self.catalog["styles"][0]["id"]
        for path in (f"styles/../{style_id}", f"/styles/{style_id}", f"C:/{style_id}"):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):
                    MODULE.portable_style_root(style_id, path)

    def test_style_reference_cannot_escape_workspace(self):
        with self.assertRaises(ValueError):
            MODULE.portable_style_reference("STYLE_TEST", "implementation", "../../../outside.html")

    def test_malformed_catalog_and_nonfinite_weights_are_rejected(self):
        cases = {
            "root": [],
            "entry": {"styles": [None]},
            "nan": {**self.catalog, "selection_weights": {"bad": float("nan")}},
            "huge": {**self.catalog, "selection_weights": {"bad": 10**4000}},
        }
        for name, catalog in cases.items():
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    MODULE.validate_styles(catalog, self.style_schema, self.motion_schema)

    def test_full_package_hash_changes_when_any_file_is_added(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "style"
            root.mkdir()
            for name in ("README.md", "motion.json", "style.json"):
                (root / name).write_text(name, encoding="utf-8")
            original = MODULE.style_package_sha256(root)
            assets = root / "assets"
            assets.mkdir()
            (assets / "theme.css").write_text("body{}", encoding="utf-8")
            self.assertNotEqual(original, MODULE.style_package_sha256(root))

    def test_style_reference_rejects_intermediate_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            styles = workspace / "framework/styles"
            target = workspace / "target"
            styles.mkdir(parents=True)
            target.mkdir()
            (target / "impl.html").write_text("ok", encoding="utf-8")
            (styles / "linked").symlink_to(target, target_is_directory=True)
            original_catalog = MODULE.STYLE_CATALOG
            original_workspace = MODULE.WORKSPACE_ROOT
            try:
                MODULE.STYLE_CATALOG = styles / "catalog.json"
                MODULE.WORKSPACE_ROOT = workspace
                with self.assertRaisesRegex(ValueError, "symlink"):
                    MODULE.portable_style_reference("STYLE_TEST", "implementation", "linked/impl.html")
            finally:
                MODULE.STYLE_CATALOG = original_catalog
                MODULE.WORKSPACE_ROOT = original_workspace

    def test_advanced_qa_schema_is_integrity_pinned(self):
        schema = MODULE.load("schemas/qa-scorecard.schema.json")
        MODULE.validate_qa_schema_contract(schema)
        modified = copy.deepcopy(schema)
        modified["title"] = "Unreviewed drift"
        with self.assertRaisesRegex(ValueError, "contract drift"):
            MODULE.validate_qa_schema_contract(modified)


class OptimizationContractValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.asset_index = MODULE.load("templates/asset-index.json")
        cls.usage_history = MODULE.load("templates/asset-usage-history.json")
        cls.recipe_catalog = MODULE.load("creative-recipes/catalog.json")
        cls.recipe_plan = MODULE.load("templates/creative-recipe-plan.json")
        cls.review = MODULE.load("templates/review-packet.json")
        cls.content_lock = MODULE.load("templates/content-lock-evidence.json")
        cls.publish = MODULE.load("templates/publish-package.json")
        cls.creative_attribution = MODULE.load("templates/creative-attribution.json")
        cls.publication_registry = MODULE.load("templates/publication-registry.json")
        cls.performance_observation = MODULE.load("templates/performance-observation.json")
        cls.performance_store = MODULE.load("templates/performance-store.json")
        cls.performance_report = MODULE.load("templates/performance-cohort-report.json")
        cls.production_metrics = MODULE.load("templates/production-metrics.json")

    def test_current_optimization_templates_are_fail_closed(self):
        self.assertEqual(
            MODULE.validate_asset_intelligence_contract(self.asset_index, self.usage_history),
            {"indexed_assets": 0, "usage_events": 0},
        )
        recipe = MODULE.validate_recipe_contract(self.recipe_catalog, self.recipe_plan)
        self.assertEqual(recipe["recipe_modules"], 18)
        self.assertEqual(recipe["recipe_proposals"], 3)
        workflow = MODULE.validate_review_and_publish_templates(
            self.review, self.content_lock, self.publish
        )
        self.assertEqual(workflow, {"review_decisions": 4, "publish_targets": 1})

    def test_asset_index_cannot_claim_perceptual_similarity(self):
        index = copy.deepcopy(self.asset_index)
        index["capabilities"]["perceptual_visual_similarity"] = True
        with self.assertRaisesRegex(ValueError, "perceptual visual similarity"):
            MODULE.validate_asset_intelligence_contract(index, self.usage_history)

    def test_asset_usage_requires_exactly_one_locator(self):
        history = copy.deepcopy(self.usage_history)
        history["events"] = [
            {
                "event_id": "USE-TEST",
                "asset_id": "IMG-TEST-0001",
                "sha256": "0" * 64,
                "video_id": "VIDEO-01",
                "video_sequence": 1,
                "used_at": "2026-09-25T00:00:00Z",
                "role": "cutaway",
                "family": None,
            }
        ]
        with self.assertRaisesRegex(ValueError, "exactly one locator"):
            MODULE.validate_asset_intelligence_contract(self.asset_index, history)

    def test_recipe_input_hash_drift_is_rejected(self):
        plan = copy.deepcopy(self.recipe_plan)
        plan["inputs"]["catalog"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "catalog hash drift"):
            MODULE.validate_recipe_contract(self.recipe_catalog, plan)

    def test_review_and_publish_templates_cannot_begin_approved(self):
        review = copy.deepcopy(self.review)
        review["decisions"]["video"]["status"] = "approved"
        with self.assertRaisesRegex(ValueError, "must begin pending"):
            MODULE.validate_review_and_publish_templates(review, self.content_lock, self.publish)

        publish = copy.deepcopy(self.publish)
        publish["status"] = "ready"
        with self.assertRaisesRegex(ValueError, "must begin blocked"):
            MODULE.validate_review_and_publish_templates(self.review, self.content_lock, publish)

        publish = copy.deepcopy(self.publish)
        publish["blocking_reasons"].append("tampered")
        with self.assertRaisesRegex(ValueError, "payload SHA-256 does not match"):
            MODULE.validate_review_and_publish_templates(self.review, self.content_lock, publish)

    def test_current_performance_templates_are_noncausal_and_reproducible(self):
        counts = MODULE.validate_performance_templates(
            self.creative_attribution,
            self.publication_registry,
            self.performance_observation,
            self.performance_store,
            self.performance_report,
            self.production_metrics,
        )
        self.assertEqual(counts["publication_records"], 1)
        self.assertEqual(counts["performance_observations"], 0)
        self.assertEqual(counts["production_template_id"], "PROD-34D2EC20F1ACFBD6")
        self.assertEqual(counts["creative_attribution_id"], "ATTR-CC2B24EE018D090C")

    def test_creative_attribution_must_select_a_real_recipe_proposal(self):
        attribution = copy.deepcopy(self.creative_attribution)
        attribution["selection"]["recipe_id"] = "RECIPE-NOT-REAL-000000000000"
        attribution["attribution_id"] = MODULE.performance_cohorts.creative_attribution_id(
            attribution
        )
        with self.assertRaisesRegex(ValueError, "exactly one real proposal"):
            MODULE.validate_performance_templates(
                attribution,
                self.publication_registry,
                self.performance_observation,
                self.performance_store,
                self.performance_report,
                self.production_metrics,
            )

    def test_performance_lineage_and_governance_drift_are_rejected(self):
        observation = copy.deepcopy(self.performance_observation)
        observation["lineage"]["delivery_sha256"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "not reproducible|lineage drifts"):
            MODULE.validate_performance_templates(
                self.creative_attribution,
                self.publication_registry,
                observation,
                self.performance_store,
                self.performance_report,
                self.production_metrics,
            )

        report = copy.deepcopy(self.performance_report)
        report["governance"]["automatic_rule_promotion"] = True
        with self.assertRaisesRegex(ValueError, "non-causal"):
            MODULE.validate_performance_templates(
                self.creative_attribution,
                self.publication_registry,
                self.performance_observation,
                self.performance_store,
                report,
                self.production_metrics,
            )

        report = copy.deepcopy(self.performance_report)
        report["report_id"] = "COHORT-REPORT-0000000000000000"
        with self.assertRaisesRegex(ValueError, "report id is not reproducible"):
            MODULE.validate_performance_templates(
                self.creative_attribution,
                self.publication_registry,
                self.performance_observation,
                self.performance_store,
                report,
                self.production_metrics,
            )


class FrameworkPlatformValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = MODULE.load("platforms/catalog.json")
        cls.profile_schema = MODULE.load("schemas/platform-profile.schema.json")

    def test_platform_catalog_and_all_profiles_are_valid(self):
        self.assertEqual(
            MODULE.validate_platform_profiles(self.catalog, self.profile_schema),
            4,
        )

    def test_safe_zone_may_not_escape_normalized_canvas(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["profiles"][1]["internal_defaults"]["safe_zones"]["essential"] = {
            "x": 0.8,
            "y": 0.1,
            "width": 0.3,
            "height": 0.7,
        }
        with self.assertRaisesRegex(ValueError, "escapes the normalized canvas"):
            MODULE.validate_platform_profiles(catalog, self.profile_schema)

    def test_required_derivative_cannot_disappear(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["profiles"] = [
            item for item in catalog["profiles"]
            if item["id"] != "PLATFORM-TIKTOK-ORGANIC-001"
        ]
        with self.assertRaisesRegex(ValueError, "missing required derivatives"):
            MODULE.validate_platform_profiles(catalog, self.profile_schema)

    def test_duplicate_platform_profile_is_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["profiles"].append(copy.deepcopy(catalog["profiles"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate platform profile"):
            MODULE.validate_platform_profiles(catalog, self.profile_schema)

    def test_official_platform_source_must_be_in_source_catalog(self):
        known_urls = {
            item["url"] for item in MODULE.load("sources/catalog.json")["sources"]
        }
        MODULE.validate_platform_profiles(self.catalog, self.profile_schema, known_urls)
        missing_one = set(known_urls)
        missing_one.remove("https://www.facebook.com/business/ads/facebook-instagram-reels-ads")
        with self.assertRaisesRegex(ValueError, "missing from sources/catalog.json"):
            MODULE.validate_platform_profiles(self.catalog, self.profile_schema, missing_one)


class TemplateBankValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = MODULE.load("template-bank/registry.json")
        cls.registry_schema = MODULE.load("schemas/template-bank-registry.schema.json")
        cls.approval_schema = MODULE.load("schemas/approval-receipt.schema.json")

    def setUp(self):
        # The light package carries code recipes, not a real approved MP4.
        # Existing approval tests get a synthetic, temporary bound artifact.
        self.registry = copy.deepcopy(type(self).registry)
        temporary = tempfile.TemporaryDirectory(dir=MODULE.WORKSPACE_ROOT)
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        artifact = folder / "synthetic-test.bin"
        artifact.write_bytes(b"synthetic approval-contract fixture; not a video")
        receipt = MODULE.approval_receipts.prepare_receipt(
            artifact, receipt_id="APPROVAL-VIDEO-01-LIGHT-TEST", project_id="TEST-PROJECT",
            video_id="VIDEO-01", media_role="editorial_mezzanine",
            profile_id="MASTER-PROFILE-EDITORIAL-HDR-001", created_at="2026-10-06T00:00:00Z",
            notes="Synthetic test fixture only; never a user approval.",
        )
        receipt["decision"] = {
            "status":"approved", "explicit_user_approval":True, "approver":"test-user",
            "decided_at":"2026-10-06T00:00:00Z", "recorded_at":"2026-10-06T00:00:00Z",
            "recorded_by":"test-suite", "evidence":{"kind":"user_message",
            "reference":"thread:test/turn:synthetic", "excerpt":"Synthetic approval fixture."},
            "scope":{"whole_artifact":True,"approved_layers":[]},
        }
        receipt = MODULE.approval_receipts.seal_receipt(receipt, artifact_override=artifact)
        receipt_path = folder / "receipt.json"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        self.registry["templates"][0]["artifact_approval"].update({
            "video_id":"VIDEO-01", "status":"approved", "scope":"whole_artifact",
            "receipt_path":receipt_path.relative_to(MODULE.WORKSPACE_ROOT).as_posix(),
        })

    def test_light_package_registry_does_not_inherit_render_approval(self):
        actual = MODULE.load("template-bank/registry.json")
        self.assertEqual(MODULE.validate_template_bank(actual,self.registry_schema,self.approval_schema),10)
        self.assertTrue(all(t["artifact_approval"]["status"] == "not_applicable" for t in actual["templates"]))

    def test_current_registry_is_valid(self):
        self.assertEqual(
            MODULE.validate_template_bank(
                self.registry,
                self.registry_schema,
                self.approval_schema,
            ),
            10,
        )

    def test_duplicate_template_id_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["templates"].append(copy.deepcopy(registry["templates"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate template id"):
            MODULE.validate_template_bank(registry, self.registry_schema, self.approval_schema)

    def test_approved_artifact_requires_existing_receipt(self):
        registry = copy.deepcopy(self.registry)
        artifact = registry["templates"][0]["artifact_approval"]
        artifact.update(
            {
                "status": "approved",
                "receipt_path": "missing/approval.json",
                "scope": "whole_artifact",
            }
        )
        with self.assertRaisesRegex(FileNotFoundError, "Missing .* approval receipt"):
            MODULE.validate_template_bank(registry, self.registry_schema, self.approval_schema)

    def test_template_default_requires_approved_source_artifact(self):
        registry = copy.deepcopy(self.registry)
        artifact = registry["templates"][0]["artifact_approval"]
        artifact.update(
            {
                "status": "pending_receipt",
                "receipt_path": None,
                "scope": None,
            }
        )
        reuse = registry["templates"][0]["template_reuse"]
        reuse.update(
            {
                "status": "series_default",
                "scope": "series",
                "authorization_basis": "explicit_template_approval",
                "authorization_ref": "thread:test/turn:template-approval",
            }
        )
        with self.assertRaisesRegex(ValueError, "independently approved source artifact"):
            MODULE.validate_template_bank(registry, self.registry_schema, self.approval_schema)

    def test_artifact_receipt_cannot_authorize_template_reuse(self):
        registry = copy.deepcopy(self.registry)
        template = registry["templates"][0]
        reuse = template["template_reuse"]
        reuse.update(
            {
                "status": "series_default",
                "scope": "series",
                "authorization_basis": "explicit_template_approval",
                "authorization_ref": template["artifact_approval"]["receipt_path"],
            }
        )
        with self.assertRaisesRegex(ValueError, "artifact receipt cannot authorize template reuse"):
            MODULE.validate_template_bank(registry, self.registry_schema, self.approval_schema)

    def test_unknown_namespace_status_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        registry["templates"][0]["performance"]["status"] = "viral"
        with self.assertRaisesRegex(ValueError, "does not match its schema"):
            MODULE.validate_template_bank(registry, self.registry_schema, self.approval_schema)

    def test_approved_artifact_can_remain_pending_for_template_reuse(self):
        registry = copy.deepcopy(self.registry)
        template = registry["templates"][0]

        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source_project = workspace / "project/source"
            source_project.mkdir(parents=True)
            artifact_path = workspace / "render.mp4"
            artifact_path.write_bytes(b"approved-render")
            receipt_path = workspace / "receipts/video-01.json"
            receipt_path.parent.mkdir()
            receipt = MODULE.approval_receipts.prepare_receipt(
                artifact_path,
                receipt_id="APPROVAL-VIDEO-01-TEST",
                project_id="TEST-PROJECT",
                video_id="VIDEO-01",
                media_role="editorial_mezzanine",
                profile_id="MASTER-PROFILE-EDITORIAL-HDR-001",
                created_at="2025-09-25T15:00:00Z",
                notes="Synthetic test fixture.",
            )
            receipt["decision"] = {
                "status": "approved",
                "explicit_user_approval": True,
                "approver": "test-user",
                "decided_at": "2025-09-24T15:00:00Z",
                "recorded_at": "2025-09-25T15:01:00Z",
                "recorded_by": "test-suite",
                "evidence": {
                    "kind": "user_message",
                    "reference": "thread:test/turn:artifact-approval",
                    "excerpt": "Aprobado.",
                },
                "scope": {"whole_artifact": True, "approved_layers": []},
            }
            receipt = MODULE.approval_receipts.seal_receipt(
                receipt,
                artifact_override=artifact_path,
            )
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            template["source_project"] = "project/source"
            template["artifact_approval"].update(
                {
                    "status": "approved",
                    "receipt_path": "receipts/video-01.json",
                    "scope": "whole_artifact",
                }
            )
            registry["templates"] = [template]
            original_workspace = MODULE.WORKSPACE_ROOT
            try:
                MODULE.WORKSPACE_ROOT = workspace
                self.assertEqual(
                    MODULE.validate_template_bank(
                        registry,
                        self.registry_schema,
                        self.approval_schema,
                    ),
                    1,
                )
                self.assertEqual(template["template_reuse"]["status"], "pending")
            finally:
                MODULE.WORKSPACE_ROOT = original_workspace

    def test_tampered_or_rebound_receipt_is_rejected(self):
        registry = copy.deepcopy(self.registry)
        template = registry["templates"][0]
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            source_project = workspace / "project/source"
            source_project.mkdir(parents=True)
            artifact_path = workspace / "render.mp4"
            artifact_path.write_bytes(b"version-one")
            receipt = MODULE.approval_receipts.prepare_receipt(
                artifact_path,
                receipt_id="APPROVAL-VIDEO-01-TAMPER",
                project_id="TEST-PROJECT",
                video_id="VIDEO-01",
                profile_id="MASTER-PROFILE-EDITORIAL-HDR-001",
                created_at="2025-09-25T15:00:00Z",
            )
            receipt["decision"] = {
                "status": "approved",
                "explicit_user_approval": True,
                "approver": "test-user",
                "decided_at": "2025-09-24T15:00:00Z",
                "recorded_at": "2025-09-25T15:01:00Z",
                "recorded_by": "test-suite",
                "evidence": {
                    "kind": "user_message",
                    "reference": "thread:test/turn:approval",
                    "excerpt": "Aprobado.",
                },
                "scope": {"whole_artifact": True, "approved_layers": []},
            }
            receipt = MODULE.approval_receipts.seal_receipt(receipt, artifact_override=artifact_path)
            receipt_path = workspace / "receipts/video-01.json"
            receipt_path.parent.mkdir()
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            artifact_path.write_bytes(b"version-two")
            template["source_project"] = "project/source"
            template["artifact_approval"]["receipt_path"] = "receipts/video-01.json"
            registry["templates"] = [template]
            original_workspace = MODULE.WORKSPACE_ROOT
            try:
                MODULE.WORKSPACE_ROOT = workspace
                with self.assertRaisesRegex(ValueError, "artifact binding failed: hash_mismatch"):
                    MODULE.validate_template_bank(
                        registry,
                        self.registry_schema,
                        self.approval_schema,
                    )
            finally:
                MODULE.WORKSPACE_ROOT = original_workspace


if __name__ == "__main__":
    unittest.main()
