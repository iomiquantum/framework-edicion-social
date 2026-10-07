#!/usr/bin/env python3

import hashlib
import importlib.util
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path


FRAMEWORK = Path(__file__).resolve().parents[2]
SCRIPT = FRAMEWORK / "scripts/asset_intelligence.py"
SPEC = importlib.util.spec_from_file_location("asset_intelligence", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SCHEMA_SPEC = importlib.util.spec_from_file_location(
    "asset_schema_validation", FRAMEWORK / "scripts/schema_validation.py"
)
SCHEMA_VALIDATOR = importlib.util.module_from_spec(SCHEMA_SPEC)
SCHEMA_SPEC.loader.exec_module(SCHEMA_VALIDATOR)


def digest(payload):
    return hashlib.sha256(payload).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def catalog_asset(
    asset_id,
    file_name,
    payload,
    *,
    asset_type="image",
    status="approved",
    tags=None,
    best_for=None,
    reuse=None,
    approval=None,
):
    value = {
        "id": asset_id,
        "name": asset_id,
        "file": file_name,
        "type": asset_type,
        "description": f"Reusable description for {asset_id}",
        "semantic_tags": tags or ["general"],
        "best_for": best_for or ["general support"],
        "avoid_for": [],
        "status": status,
        "sha256": digest(payload),
        "provenance": {"kind": "test", "license": "test"},
        "reuse": reuse
        or {
            "policy": "rotate",
            "cooldown_videos": 1,
            "usage_count": 0,
            "last_used_at": None,
            "used_in": [],
        },
    }
    if approval is not None:
        value["approval"] = approval
    return value


class AssetIntelligenceTests(unittest.TestCase):
    def make_project(self, temporary):
        project = Path(temporary) / "project"
        project.mkdir()
        return project

    def test_templates_match_dependency_free_schemas(self):
        for name in ("asset-index", "asset-usage-history"):
            with self.subTest(name=name):
                template = json.loads(
                    (FRAMEWORK / f"templates/{name}.json").read_text(encoding="utf-8")
                )
                schema = json.loads(
                    (FRAMEWORK / f"schemas/{name}.schema.json").read_text(encoding="utf-8")
                )
                self.assertEqual(SCHEMA_VALIDATOR.validate_document(template, schema), [])

    def test_catalog_and_media_use_copies_merge_by_exact_sha(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            payload = b"same-waveform"
            library_file = project / "library/soft.wav"
            library_file.parent.mkdir()
            library_file.write_bytes(payload)
            catalog = project / "library/catalog.json"
            write_json(
                catalog,
                {
                    "assets": [
                        catalog_asset(
                            "SFX-SOFT-0001",
                            "soft.wav",
                            payload,
                            asset_type="sfx",
                            tags=["suave", "transicion"],
                        )
                    ]
                },
            )
            media_file = project / ".media/audio/sfx/copy.wav"
            media_file.parent.mkdir(parents=True)
            media_file.write_bytes(payload)
            media_manifest = project / ".media/manifest.jsonl"
            media_manifest.write_text(
                json.dumps(
                    {
                        "id": "sfx_001",
                        "type": "sfx",
                        "path": ".media/audio/sfx/copy.wav",
                        "source": "ingested",
                        "description": "soft transition",
                        "provenance": {"provider": "local"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            index = MODULE.build_index(
                project_root=project,
                catalogs=[catalog],
                manifests=[media_manifest],
                discover_media_use=False,
                generated_at="2026-09-25T00:00:00Z",
            )

            self.assertEqual(index["summary"]["asset_count"], 1)
            self.assertEqual(index["summary"]["source_record_count"], 2)
            self.assertEqual(index["assets"][0]["asset_id"], "SFX-SOFT-0001")
            self.assertEqual(len(index["assets"][0]["provenance_records"]), 2)
            self.assertEqual(index["exact_duplicate_groups"][0]["proof"], "exact_sha256")
            self.assertEqual(len(index["exact_duplicate_groups"][0]["locations"]), 2)

    def test_media_use_discovery_is_automatic_and_skips_node_modules(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            media_file = project / "clip/.media/images/asset.png"
            media_file.parent.mkdir(parents=True)
            media_file.write_bytes(b"image")
            (project / "clip/.media/manifest.jsonl").write_text(
                json.dumps(
                    {
                        "id": "image_001",
                        "type": "image",
                        "path": ".media/images/asset.png",
                        "description": "automation concept",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            ignored = project / "node_modules/pkg/.media"
            ignored.mkdir(parents=True)
            (ignored / "manifest.jsonl").write_text("not-json\n", encoding="utf-8")

            index = MODULE.build_index(
                project_root=project,
                discover_media_use=True,
                generated_at="2026-09-25T00:00:00Z",
            )
            self.assertEqual(index["summary"]["asset_count"], 1)
            self.assertTrue(index["assets"][0]["asset_id"].startswith("AUTO-IMAGE-"))

    def test_media_use_local_ids_are_namespaced_across_projects(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            manifests = []
            for folder, payload in (("one", b"first"), ("two", b"second")):
                media = project / folder / ".media"
                asset = media / "images/item.png"
                asset.parent.mkdir(parents=True)
                asset.write_bytes(payload)
                manifest = media / "manifest.jsonl"
                manifest.write_text(
                    json.dumps(
                        {
                            "id": "image_001",
                            "type": "image",
                            "path": ".media/images/item.png",
                            "description": "project-local image",
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )
                manifests.append(manifest)

            index = MODULE.build_index(
                project_root=project,
                manifests=manifests,
                discover_media_use=False,
            )
            self.assertEqual(index["summary"]["asset_count"], 2)
            self.assertEqual(len({asset["asset_id"] for asset in index["assets"]}), 2)
            self.assertTrue(
                all("::image_001" in asset["source_asset_ids"][0] for asset in index["assets"])
            )

    def test_declared_hash_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            media = project / "library/item.png"
            media.parent.mkdir()
            media.write_bytes(b"current")
            asset = catalog_asset("IMG-TEST-0001", "item.png", b"previous")
            catalog = project / "library/catalog.json"
            write_json(catalog, {"assets": [asset]})
            with self.assertRaisesRegex(MODULE.AssetIndexError, "Hash mismatch"):
                MODULE.build_index(
                    project_root=project,
                    catalogs=[catalog],
                    discover_media_use=False,
                )

    def test_same_asset_id_cannot_point_to_two_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            library = project / "library"
            library.mkdir()
            (library / "one.png").write_bytes(b"one")
            (library / "two.png").write_bytes(b"two")
            catalog = library / "catalog.json"
            write_json(
                catalog,
                {
                    "assets": [
                        catalog_asset("IMG-DUP-0001", "one.png", b"one"),
                        catalog_asset("IMG-DUP-0001", "two.png", b"two"),
                    ]
                },
            )
            with self.assertRaisesRegex(MODULE.AssetIndexError, "multiple hashes"):
                MODULE.build_index(
                    project_root=project,
                    catalogs=[catalog],
                    discover_media_use=False,
                )

    def test_query_excludes_rejected_deprecated_and_do_not_reuse(self):
        index = self.query_index_doc(
            [
                self.query_asset("APPROVED", "approved"),
                self.query_asset("DEPRECATED", "deprecated"),
                self.query_asset("REJECTED", "rejected"),
                self.query_asset("NO-REUSE", "approved", reuse_policy="do_not_reuse"),
            ]
        )
        report = MODULE.query_index(index, intent="automation", asset_type="image")
        self.assertEqual([item["asset_id"] for item in report["results"]], ["APPROVED"])
        self.assertEqual(report["excluded"]["deprecated"], 1)
        self.assertEqual(report["excluded"]["rejected"], 1)
        self.assertEqual(report["excluded"]["do_not_reuse"], 1)

    def query_asset(
        self,
        asset_id,
        status="approved",
        *,
        asset_type="image",
        reuse_policy="rotate",
        cooldown=2,
        usage_count=0,
        last_sequence=None,
        last_used_at=None,
        avoid_for=None,
    ):
        return {
            "asset_id": asset_id,
            "source_asset_ids": [],
            "name": f"Automation {asset_id}",
            "type": asset_type,
            "format": "png",
            "bytes": 10,
            "status": status,
            "sha256": digest(asset_id.encode()),
            "description": "automation workflow visual",
            "semantic_tags": ["automation", "workflow"],
            "intent_phrases": ["automation workflow"],
            "avoid_for": avoid_for or [],
            "locations": [f"assets/{asset_id}.png"],
            "metadata": {"technical": {}, "approval": {}},
            "provenance_records": [
                {
                    "source_kind": "explicit_folder",
                    "source_ref": "assets",
                    "source_asset_id": None,
                    "path": f"assets/{asset_id}.png",
                    "details": {},
                }
            ],
            "reuse": {
                "policy": reuse_policy,
                "cooldown_videos": cooldown,
                "cooldown_enforcement": "advisory_non_blocking",
            },
            "usage": {
                "usage_count": usage_count,
                "used_in": [],
                "last_used_at": last_used_at,
                "last_used_sequence": last_sequence,
                "events": [],
            },
        }

    def query_index_doc(self, assets):
        index = json.loads(
            (FRAMEWORK / "templates/asset-index.json").read_text(encoding="utf-8")
        )
        index["assets"] = assets
        index["summary"].update({
            "asset_count": len(assets),
            "source_record_count": len(assets),
            "status_counts": {
                status: sum(asset["status"] == status for asset in assets)
                for status in sorted({asset["status"] for asset in assets})
            },
            "type_counts": {
                asset_type: sum(asset["type"] == asset_type for asset in assets)
                for asset_type in sorted({asset["type"] for asset in assets})
            },
        })
        return index

    def test_ranking_is_deterministic_and_uses_declared_metadata(self):
        index = self.query_index_doc(
            [
                self.query_asset("BETA", "provisional"),
                self.query_asset("ALPHA", "approved"),
            ]
        )
        first = MODULE.query_index(index, intent="automation workflow", asset_type="image")
        second = MODULE.query_index(index, intent="automation workflow", asset_type="image")
        self.assertEqual(first, second)
        self.assertEqual(first["results"][0]["asset_id"], "ALPHA")
        self.assertEqual(first["method"]["ranking"], "deterministic_declared_metadata")
        self.assertFalse(first["method"]["auto_reuse"])

    def test_query_validates_index_schema_before_ranking(self):
        index = self.query_index_doc([self.query_asset("VALID")])
        index["assets"][0]["usage"]["last_used_at"] = "not-a-date"
        with self.assertRaisesRegex(MODULE.AssetIndexError, "Invalid asset index"):
            MODULE.query_index(index, intent="automation", asset_type="image")

    def test_avoid_for_excludes_full_constraint_and_penalizes_partial_overlap(self):
        incompatible = self.query_asset(
            "NO-FINANCE", avoid_for=["automation financiera"]
        )
        partial = self.query_asset(
            "REVIEW-FINANCE", avoid_for=["finanzas reguladas"]
        )
        clear = self.query_asset("CLEAR")
        report = MODULE.query_index(
            self.query_index_doc([incompatible, partial, clear]),
            intent="automation financiera sobre finanzas para redes",
            asset_type="image",
        )
        by_id = {item["asset_id"]: item for item in report["results"]}
        self.assertNotIn("NO-FINANCE", by_id)
        self.assertEqual(report["excluded"]["avoid_for_incompatible"], 1)
        detail = report["exclusion_details"][0]
        self.assertEqual(detail["asset_id"], "NO-FINANCE")
        self.assertEqual(detail["matched_constraints"], ["automation financiera"])
        self.assertEqual(by_id["REVIEW-FINANCE"]["avoidance"]["action"], "penalized")
        self.assertLess(by_id["REVIEW-FINANCE"]["score"], by_id["CLEAR"]["score"])
        self.assertIn(
            "avoid_for_partial_match_review_required",
            by_id["REVIEW-FINANCE"]["warnings"],
        )
        self.assertIn("Exclude complete declared incompatibilities", report["method"]["avoid_for_policy"])

    def test_cooldown_warns_and_penalizes_without_blocking(self):
        fresh = self.query_asset(
            "RECENT", usage_count=1, last_sequence=1, cooldown=2
        )
        old = self.query_asset(
            "OLDER", usage_count=1, last_sequence=4, cooldown=1
        )
        report = MODULE.query_index(
            self.query_index_doc([fresh, old]),
            intent="automation workflow",
            asset_type="image",
            current_video_sequence=2,
        )
        by_id = {item["asset_id"]: item for item in report["results"]}
        self.assertIn("RECENT", by_id)
        self.assertEqual(by_id["RECENT"]["fatigue"]["status"], "within_cooldown")
        self.assertFalse(by_id["RECENT"]["fatigue"]["blocking"])
        self.assertIn("advisory_cooldown_active", by_id["RECENT"]["warnings"])
        self.assertEqual(by_id["OLDER"]["fatigue"]["status"], "sequence_conflict")

    def test_last_used_at_is_real_datetime_and_merged_chronologically(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            library = project / "library"
            library.mkdir()
            payload = b"same"
            (library / "one.png").write_bytes(payload)
            (library / "two.png").write_bytes(payload)
            first = catalog_asset("IMG-TIME-0001", "one.png", payload)
            second = catalog_asset("IMG-TIME-0002", "two.png", payload)
            first["reuse"]["last_used_at"] = "2026-09-25T23:00:00-05:00"
            second["reuse"]["last_used_at"] = "2026-09-26T03:30:00Z"
            catalog = library / "catalog.json"
            write_json(catalog, {"assets": [first, second]})
            index = MODULE.build_index(
                project_root=project,
                catalogs=[catalog],
                discover_media_use=False,
            )
            self.assertEqual(
                index["assets"][0]["usage"]["last_used_at"],
                "2026-09-26T04:00:00Z",
            )

            first["reuse"]["last_used_at"] = "2026-02-31T12:00:00Z"
            write_json(catalog, {"assets": [first]})
            with self.assertRaisesRegex(MODULE.AssetIndexError, "valid RFC 3339 date-time"):
                MODULE.build_index(
                    project_root=project,
                    catalogs=[catalog],
                    discover_media_use=False,
                )

    def test_index_explicitly_disclaims_perceptual_visual_similarity(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            index = MODULE.build_index(
                project_root=project,
                discover_media_use=False,
                generated_at="2026-09-25T00:00:00Z",
            )
            self.assertFalse(index["capabilities"]["perceptual_visual_similarity"])
            self.assertIn("No perceptual visual similarity", index["capabilities"]["similarity_notice"])

    def test_usage_history_is_merged_by_exactly_one_locator(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            library = project / "library"
            library.mkdir()
            payload = b"asset"
            (library / "asset.png").write_bytes(payload)
            catalog = library / "catalog.json"
            write_json(
                catalog,
                {"assets": [catalog_asset("IMG-AUTO-0001", "asset.png", payload)]},
            )
            history = project / "usage.json"
            write_json(
                history,
                {
                    "schema_version": "1.0.0",
                    "updated_at": "2026-09-25T00:00:00Z",
                    "events": [
                        {
                            "event_id": "USE-0001",
                            "asset_id": "IMG-AUTO-0001",
                            "video_id": "VIDEO-03",
                            "video_sequence": 3,
                            "used_at": "2026-09-25T01:00:00Z",
                            "role": "cutaway",
                            "family": "automation",
                        }
                    ],
                },
            )
            index = MODULE.build_index(
                project_root=project,
                catalogs=[catalog],
                usage_history=history,
                discover_media_use=False,
            )
            usage = index["assets"][0]["usage"]
            self.assertEqual(usage["last_used_sequence"], 3)
            self.assertEqual(usage["used_in"], ["VIDEO-03"])
            self.assertEqual(usage["events"][0]["event_id"], "USE-0001")

            invalid = json.loads(history.read_text(encoding="utf-8"))
            invalid["events"][0]["sha256"] = digest(payload)
            write_json(history, invalid)
            with self.assertRaisesRegex(MODULE.AssetIndexError, "exactly one"):
                MODULE.build_index(
                    project_root=project,
                    catalogs=[catalog],
                    usage_history=history,
                    discover_media_use=False,
                )

    def test_explicit_folder_rejects_symlinked_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            assets = project / "assets"
            assets.mkdir()
            outside = project / "outside.png"
            outside.write_bytes(b"outside")
            (assets / "linked.png").symlink_to(outside)
            with self.assertRaisesRegex(MODULE.AssetIndexError, "Symlink file"):
                MODULE.build_index(
                    project_root=project,
                    roots=[assets],
                    discover_media_use=False,
                )

    def test_cli_only_writes_to_explicit_safe_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(temporary)
            output = project / "reports/index.json"
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = MODULE.main(
                    [
                        "build",
                        "--project-root",
                        str(project),
                        "--no-discover-media-use",
                        "--generated-at",
                        "2026-09-25T00:00:00Z",
                        "--out",
                        str(output),
                    ]
                )
            self.assertEqual(code, 0, stderr.getvalue())
            self.assertTrue(output.is_file())
            self.assertIn("OK:", stdout.getvalue())

            outside = Path(temporary) / "outside.json"
            with redirect_stdout(StringIO()), redirect_stderr(stderr):
                code = MODULE.main(
                    [
                        "build",
                        "--project-root",
                        str(project),
                        "--no-discover-media-use",
                        "--out",
                        str(outside),
                    ]
                )
            self.assertEqual(code, 2)
            self.assertFalse(outside.exists())


if __name__ == "__main__":
    unittest.main()
