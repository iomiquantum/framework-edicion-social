#!/usr/bin/env python3

import copy
import importlib.util
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path


FRAMEWORK = Path(__file__).resolve().parents[2]
SCRIPT = FRAMEWORK / "scripts/plan_platform_derivatives.py"
SPEC = importlib.util.spec_from_file_location("plan_platform_derivatives", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CATALOG_PATH = FRAMEWORK / "platforms/catalog.json"
MASTER_TEMPLATE = FRAMEWORK / "templates/platform-master.json"
ADAPTATION_TEMPLATE = FRAMEWORK / "templates/platform-adaptation.json"


def approved_master():
    master = json.loads(MASTER_TEMPLATE.read_text(encoding="utf-8"))
    master["approval"] = {
        "status": "approved",
        "explicit_user_approval": True,
        "approved_by": "owner",
        "approved_at": "2026-09-25T12:00:00Z",
        "note": "Aprobado explicitamente.",
    }
    master["content_lock"] = {
        "status": "locked",
        "locked_at": "2026-09-25T12:01:00Z",
        "take": True,
        "cuts": True,
        "voice": True,
        "semantics": True,
        "assets": True,
    }
    master["hashes"] = {
        "project_sha256": "a" * 64,
        "cut_plan_sha256": "b" * 64,
        "audio_mix_sha256": "c" * 64,
    }
    return master


class PlatformDerivativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = MODULE.load_catalog(CATALOG_PATH)

    def test_catalog_contains_one_master_and_three_platform_derivatives(self):
        profiles = self.catalog["profiles"]
        self.assertEqual(len(profiles), 4)
        self.assertEqual(sum(item["kind"] == "master" for item in profiles), 1)
        self.assertEqual(
            {item["platform"] for item in profiles if item["kind"] == "derivative"},
            {"instagram", "tiktok", "youtube"},
        )

    def test_every_safe_zone_is_internal_conservative_and_bounded(self):
        for profile in self.catalog["profiles"]:
            zones = profile["internal_defaults"]["safe_zones"]
            self.assertEqual(zones["provenance"], "internal_conservative_not_official")
            self.assertTrue(zones["requires_live_preview"])
            for name in ("action", "title", "essential", "captions"):
                rect = zones[name]
                self.assertLessEqual(rect["x"] + rect["width"], 1)
                self.assertLessEqual(rect["y"] + rect["height"], 1)

    def test_ad_platform_evidence_is_not_mislabeled_as_organic_requirement(self):
        by_platform = {item["platform"]: item for item in self.catalog["profiles"]}
        self.assertIn("publicitario", by_platform["instagram"]["official_constraints"]["scope_notice"])
        self.assertIn("publicitarias", by_platform["tiktok"]["official_constraints"]["scope_notice"])
        for platform in ("instagram", "tiktok"):
            for claim in by_platform[platform]["official_constraints"]["claims"]:
                self.assertIn("scope", claim)
                self.assertTrue(claim["source_url"].startswith("https://"))

    def test_pending_master_is_blocked_before_any_platform_work(self):
        master = json.loads(MASTER_TEMPLATE.read_text(encoding="utf-8"))
        plan = MODULE.build_plan(master, self.catalog)
        self.assertEqual(plan["status"], "blocked_until_master_approved")
        self.assertEqual(len(plan["targets"]), 1)
        self.assertEqual(plan["targets"][0]["platform"], "instagram")
        self.assertTrue(all(item["status"] == "blocked" for item in plan["targets"]))
        self.assertTrue(all(item["gates"][0]["status"] == "pending" for item in plan["targets"]))

    def test_approved_but_unlocked_master_is_still_blocked(self):
        master = approved_master()
        master["content_lock"] = {
            "status": "unlocked",
            "locked_at": None,
            "take": False,
            "cuts": False,
            "voice": False,
            "semantics": False,
            "assets": False,
        }
        master["hashes"] = {
            "project_sha256": None,
            "cut_plan_sha256": None,
            "audio_mix_sha256": None,
        }
        plan = MODULE.build_plan(master, self.catalog)
        self.assertEqual(plan["status"], "blocked_until_content_locked")
        self.assertEqual(plan["blocking_reasons"], ["El contenido o sus hashes no estan completamente bloqueados."])

    def test_approved_locked_master_creates_delta_only_preview_plan(self):
        plan = MODULE.build_plan(approved_master(), self.catalog)
        self.assertEqual(plan["status"], "ready_for_platform_preview")
        self.assertEqual(plan["blocking_reasons"], [])
        self.assertEqual(
            plan["policy"]["strategy"],
            "instagram_master_reuse_unless_material_delta",
        )
        self.assertEqual(
            set(plan["policy"]["preserve"]),
            {"take", "cuts", "voice", "semantics", "approved_assets"},
        )
        self.assertEqual(len(plan["targets"]), 1)
        self.assertEqual(plan["targets"][0]["platform"], "instagram")
        for target in plan["targets"]:
            self.assertEqual(target["status"], "ready_for_preview")
            statuses = {gate["id"]: gate["status"] for gate in target["gates"]}
            self.assertEqual(statuses["explicit_master_approval"], "passed")
            self.assertEqual(statuses["content_lock"], "passed")
            self.assertEqual(statuses["live_platform_preview"], "pending")
            self.assertEqual(statuses["semantic_match"], "pending")
            self.assertEqual(target["safe_zone"]["provenance"], "internal_conservative_not_official")

    def test_single_target_selection_does_not_create_other_edits(self):
        target_id = "PLATFORM-YOUTUBE-SHORTS-001"
        plan = MODULE.build_plan(approved_master(), self.catalog, target_ids=[target_id])
        self.assertEqual([item["profile_id"] for item in plan["targets"]], [target_id])
        self.assertEqual(plan["targets"][0]["platform"], "youtube")

    def test_multiple_platforms_require_explicit_target_selection(self):
        target_ids = [
            "PLATFORM-INSTAGRAM-REELS-ORGANIC-001",
            "PLATFORM-TIKTOK-ORGANIC-001",
            "PLATFORM-YOUTUBE-SHORTS-001",
        ]
        default_plan = MODULE.build_plan(approved_master(), self.catalog)
        explicit_plan = MODULE.build_plan(
            approved_master(), self.catalog, target_ids=target_ids
        )
        self.assertEqual(len(default_plan["targets"]), 1)
        self.assertEqual(len(explicit_plan["targets"]), 3)

    def test_approval_and_lock_inconsistencies_fail_closed(self):
        master = approved_master()
        master["approval"]["explicit_user_approval"] = False
        with self.assertRaisesRegex(MODULE.PlatformPlanError, "explicit_user_approval"):
            MODULE.build_plan(master, self.catalog)

        master = approved_master()
        master["content_lock"]["semantics"] = False
        with self.assertRaisesRegex(MODULE.PlatformPlanError, "every lock flag"):
            MODULE.build_plan(master, self.catalog)

    def test_master_technical_drift_fails_closed(self):
        master = approved_master()
        master["technical"]["width"] = 720
        with self.assertRaisesRegex(MODULE.PlatformPlanError, "technical profile mismatch"):
            MODULE.build_plan(master, self.catalog)

    def test_missing_hash_blocks_even_when_lock_flags_are_true(self):
        master = approved_master()
        master["hashes"]["audio_mix_sha256"] = None
        plan = MODULE.build_plan(master, self.catalog)
        self.assertEqual(plan["status"], "blocked_until_content_locked")

    def test_unknown_and_master_targets_are_rejected(self):
        with self.assertRaisesRegex(MODULE.PlatformPlanError, "unknown target"):
            MODULE.build_plan(approved_master(), self.catalog, ["PLATFORM-NOPE-001"])
        with self.assertRaisesRegex(MODULE.PlatformPlanError, "not an active derivative"):
            MODULE.build_plan(
                approved_master(), self.catalog, ["PLATFORM-MASTER-VERTICAL-001"]
            )

    def test_invalid_safe_rectangle_is_rejected(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["profiles"][1]["internal_defaults"]["safe_zones"]["essential"]["width"] = 0.99
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            path.write_text(json.dumps(catalog), encoding="utf-8")
            with self.assertRaisesRegex(MODULE.PlatformPlanError, "right edge"):
                MODULE.load_catalog(path)

    def test_templates_match_their_schemas(self):
        schema_module = __import__("schema_validation")
        master_schema = schema_module.load_json(FRAMEWORK / "schemas/platform-master.schema.json")
        adaptation_schema = schema_module.load_json(
            FRAMEWORK / "schemas/platform-adaptation.schema.json"
        )
        master_errors = schema_module.validate_document(
            json.loads(MASTER_TEMPLATE.read_text(encoding="utf-8")), master_schema
        )
        adaptation_errors = schema_module.validate_document(
            json.loads(ADAPTATION_TEMPLATE.read_text(encoding="utf-8")), adaptation_schema
        )
        self.assertEqual(master_errors, [])
        self.assertEqual(adaptation_errors, [])

    def test_cli_writes_blocked_plan_and_returns_three(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "plan.json"
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = MODULE.main(
                    [
                        "--master",
                        str(MASTER_TEMPLATE),
                        "--catalog",
                        str(CATALOG_PATH),
                        "--out",
                        str(output),
                    ]
                )
            self.assertEqual(code, 3)
            self.assertTrue(output.is_file())
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8"))["status"],
                "blocked_until_master_approved",
            )
            self.assertIn("BLOCKED", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
