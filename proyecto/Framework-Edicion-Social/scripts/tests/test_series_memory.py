#!/usr/bin/env python3

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
FRAMEWORK = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import approval_receipt as RECEIPTS  # noqa: E402
import schema_validation as VALIDATOR  # noqa: E402
import series_memory as MODULE  # noqa: E402


def template(name):
    return json.loads((FRAMEWORK / f"templates/{name}.json").read_text(encoding="utf-8"))


class SeriesMemoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="series-memory-test-", dir=FRAMEWORK)
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def contract_and_ledger(self, series_id="series-test"):
        contract = template("series-contract")
        ledger = template("series-variety-ledger")
        contract["series_id"] = series_id
        ledger["series_id"] = series_id
        return contract, ledger

    def _approve(self, video_id, artifact):
        pending = RECEIPTS.prepare_receipt(
            artifact,
            receipt_id=f"APPROVAL-{video_id}-TEST",
            project_id="series-test",
            video_id=video_id,
            created_at="2025-01-01T11:00:00Z",
        )
        pending["decision"] = {
            "status": "approved",
            "explicit_user_approval": True,
            "approver": "owner",
            "decided_at": "2025-01-01T12:00:00Z",
            "recorded_at": "2025-01-01T12:05:00Z",
            "recorded_by": "codex-test",
            "evidence": {
                "kind": "user_message",
                "reference": f"thread:test/turn:{video_id}",
                "excerpt": "Aprobado este archivo exacto.",
            },
            "scope": {"whole_artifact": True, "approved_layers": []},
        }
        return RECEIPTS.seal_receipt(pending, artifact_override=artifact)

    def fingerprint(
        self,
        video_id,
        *,
        approved=False,
        series_id="series-test",
        aspect="9:16",
        speed=1.04,
        family_id="FAMILY-EDITORIAL-LOOP",
        archetype="ARCH-CONTRARIAN-LOOP",
        palette=None,
        parent_fingerprint_id=None,
        technical_qa="pass",
        storage_key=None,
    ):
        video_dir = self.root / (storage_key or video_id)
        video_dir.mkdir(parents=True, exist_ok=True)
        source = video_dir / "source.json"
        source.write_text(json.dumps({"video_id": video_id, "series_id": series_id}), encoding="utf-8")
        source_files = [{
            "role": "project_manifest",
            "path": MODULE._portable_path(source),
            "sha256": MODULE.file_sha256(source),
        }]
        approval = {
            "status": "unreviewed",
            "approval_ref": None,
            "approval_receipt_path": None,
            "approval_receipt_sha256": None,
            "approved_artifact_sha256": None,
        }
        qa_evidence = MODULE._technical_qa_evidence({}, None)
        if approved:
            artifact = video_dir / "approved.mp4"
            artifact.write_bytes(f"approved-{video_id}".encode())
            artifact_sha = MODULE.file_sha256(artifact)
            if technical_qa != "no_manifest":
                render = {
                    "video_id": video_id,
                    "output": {"path": artifact.name, "sha256": artifact_sha},
                }
                if technical_qa == "pass":
                    render["qa"] = {
                        "hyperframes_check": "pass",
                        "lint_errors": 0,
                        "runtime_errors": 0,
                        "layout_errors": 0,
                    }
                elif technical_qa == "fail":
                    render["qa"] = {
                        "hyperframes_check": "pass",
                        "lint_errors": 1,
                        "runtime_errors": 0,
                        "layout_errors": 0,
                    }
                elif technical_qa != "unavailable":
                    raise AssertionError(f"unsupported technical_qa fixture: {technical_qa}")
                render_path = video_dir / "manifest-render.json"
                render_path.write_text(json.dumps(render, indent=2) + "\n", encoding="utf-8")
                source_files.append({
                    "role": "render_manifest",
                    "path": MODULE._portable_path(render_path),
                    "sha256": MODULE.file_sha256(render_path),
                })
                qa_evidence = MODULE._technical_qa_evidence(render, render_path)
            receipt = self._approve(video_id, artifact)
            receipt_path = video_dir / "approval.json"
            receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            approval = {
                "status": "approved",
                "approval_ref": receipt["receipt_id"],
                "approval_receipt_path": MODULE._portable_path(receipt_path),
                "approval_receipt_sha256": MODULE.file_sha256(receipt_path),
                "approved_artifact_sha256": artifact_sha,
            }
        fp = {
            "schema_version": "1.0.0",
            "series_id": series_id,
            "video_id": video_id,
            "recorded_at": "2025-01-01",
            "approval": approval,
            "technical_qa": qa_evidence,
            "family": {
                "family_id": family_id,
                "archetype_id": archetype,
                "parent_fingerprint_id": parent_fingerprint_id,
            },
            "source_files": source_files,
            "fields": {
                "technical.aspect_ratio": aspect,
                "edit.speed": speed,
                "creative.family_id": family_id,
                "creative.archetype_id": archetype,
            },
            "traits": {
                "palette": palette if palette is not None else ["#6C63FF", "#20D6C7"],
                "semantic_tags": ["topic"],
            },
            "limitations": ["fingerprint_is_descriptive_not_a_quality_score"],
        }
        fp["fingerprint_id"] = MODULE.expected_fingerprint_id(fp)
        ordered = {key: fp[key] for key in (
            "schema_version", "fingerprint_id", "series_id", "video_id", "recorded_at",
            "approval", "technical_qa", "family", "source_files", "fields", "traits", "limitations",
        )}
        path = video_dir / "fingerprint.json"
        path.write_text(json.dumps(ordered, indent=2) + "\n", encoding="utf-8")
        MODULE.validate_fingerprint(ordered)
        return ordered, path

    def add(self, ledger, fingerprint, path):
        return MODULE.add_fingerprint_to_ledger(ledger, fingerprint, path)

    def test_templates_match_supported_schemas_and_semantics(self):
        for name in ("series-contract", "series-variety-ledger"):
            document = template(name)
            schema = json.loads((FRAMEWORK / f"schemas/{name}.schema.json").read_text(encoding="utf-8"))
            self.assertEqual(VALIDATOR.validate_document(document, schema), [])
        MODULE.validate_contract(template("series-contract"))
        MODULE.validate_ledger(template("series-variety-ledger"))
        selectors = {item["selector"] for item in template("series-contract")["dimensions"]}
        self.assertNotIn("narrative.hook_copy", selectors)
        self.assertEqual(
            {item["classification"] for item in template("series-contract")["dimensions"]},
            {"locked", "bounded", "rotating", "free"},
        )

    def test_extracts_real_sources_without_inferred_approval(self):
        project = self.root / "VIDEO-01"
        editable = project / "editable"
        editable.mkdir(parents=True)
        (project / "manifest.json").write_text(json.dumps({
            "project_id": "series-test", "video_id": "VIDEO-01",
            "target": {"aspect_ratio": "9:16", "frame": "1080x1920", "language": "es"},
            "resources": [{"id": "SFX-TEST-0001", "type": "sfx", "semantic_tags": ["soft"]}],
        }), encoding="utf-8")
        (editable / "manifest-render-v2.json").write_text(json.dumps({
            "video_id": "VIDEO-01", "edit": {"speed": 1.04}, "output": {"duration_s": 20},
        }), encoding="utf-8")
        (editable / "index.html").write_text(
            '<div data-composition-id="scene-hook" style="color:#6c63ff;font-family:Inter"></div>',
            encoding="utf-8",
        )
        extracted = MODULE.extract_fingerprint(
            editable, recorded_at="2026-09-25",
            family_id="FAMILY-EDITORIAL-LOOP", archetype_id="ARCH-CONTRARIAN-LOOP",
        )
        self.assertEqual(extracted["series_id"], "series-test")
        self.assertEqual(extracted["approval"]["status"], "unreviewed")
        self.assertEqual(extracted["traits"]["palette"], ["#6C63FF"])
        for dimension in template("series-contract")["dimensions"]:
            self.assertIn(dimension["selector"], extracted[dimension["value_source"]])
        MODULE.validate_fingerprint(extracted)

    def test_seed_is_reference_and_explicit_locked_can_block(self):
        contract, ledger = self.contract_and_ledger()
        candidate, _ = self.fingerprint("VIDEO-02", aspect="1:1")
        self.assertFalse(MODULE.check_fingerprint(contract, candidate, ledger)["blocking"])
        contract["dimensions"][0].update(state="explicit", source="explicit_instruction", enforcement="block")
        contract["dimensions"][0]["evidence"].append({
            "video_id": None, "fingerprint_id": None, "approval_ref": None, "instruction_ref": "USER-001",
        })
        self.assertTrue(MODULE.check_fingerprint(contract, candidate, ledger)["blocking"])

    def test_similarity_rotation_and_novelty_never_block_quality(self):
        contract, ledger = self.contract_and_ledger()
        prior, prior_path = self.fingerprint("VIDEO-01", approved=True)
        ledger = self.add(ledger, prior, prior_path)
        candidate, _ = self.fingerprint("VIDEO-02")
        report = MODULE.check_fingerprint(contract, candidate, ledger)
        self.assertFalse(report["variety"]["blocking"])
        self.assertFalse(report["blocking"])
        self.assertEqual(report["quality"]["conclusion"], "not_assessed")
        rotating = next(item for item in contract["dimensions"] if item["classification"] == "rotating")
        rotating.update(state="explicit", source="explicit_instruction", enforcement="block")
        rotating["evidence"] = [{
            "video_id": None, "fingerprint_id": None, "approval_ref": None, "instruction_ref": "USER-ROTATE",
        }]
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "never block"):
            MODULE.validate_contract(contract)

    def test_rechecking_fingerprint_already_in_ledger_excludes_itself(self):
        contract, ledger = self.contract_and_ledger()
        fingerprint, path = self.fingerprint("VIDEO-01", approved=True)
        ledger = self.add(ledger, fingerprint, path)

        report = MODULE.check_fingerprint(contract, fingerprint, ledger)

        self.assertEqual(report["issues"], [])
        self.assertEqual(report["variety"]["comparisons"], [])
        self.assertIsNone(report["variety"]["maximum_similarity"])
        self.assertEqual(report["variety"]["similarity_signal"], "insufficient_history")
        novelty = report["variety"]["novelty_budget"]
        self.assertEqual(novelty["status"], "insufficient_history")
        self.assertIsNone(novelty.get("predecessor_video_id"))
        self.assertEqual(novelty.get("compared_video_ids", []), [])

    def test_exact_self_exclusion_preserves_a_distinct_revision_of_same_video(self):
        contract, ledger = self.contract_and_ledger()
        prior, prior_path = self.fingerprint(
            "VIDEO-01", approved=True, palette=["#111111"], storage_key="VIDEO-01-REV1"
        )
        ledger = self.add(ledger, prior, prior_path)
        candidate, _ = self.fingerprint(
            "VIDEO-01", palette=["#222222"], storage_key="VIDEO-01-REV2"
        )

        report = MODULE.check_fingerprint(contract, candidate, ledger)

        self.assertNotEqual(candidate["fingerprint_id"], prior["fingerprint_id"])
        self.assertEqual(
            [item["video_id"] for item in report["variety"]["comparisons"]],
            ["VIDEO-01"],
        )
        self.assertEqual(
            report["variety"]["novelty_budget"]["predecessor_video_id"], "VIDEO-01"
        )

    def test_two_verified_distinct_approvals_promote_only_stable_dimensions(self):
        contract, ledger = self.contract_and_ledger()
        for video_id in ("VIDEO-01", "VIDEO-02"):
            fp, path = self.fingerprint(video_id, approved=True)
            ledger = self.add(ledger, fp, path)
        by_id = {item["dimension_id"]: item for item in MODULE.build_learning_plan(contract, ledger)["promotion_recommendations"]}
        self.assertTrue(by_id["DIM-ASPECT-RATIO"]["eligible"])
        self.assertTrue(by_id["DIM-PLAYBACK-SPEED"]["eligible"])
        self.assertEqual(by_id["DIM-NARRATIVE-ARCHETYPE"]["action"], "keep_rotating_collect_family_evidence")
        self.assertEqual(MODULE.promote_dimension(contract, ledger, "DIM-ASPECT-RATIO")["dimensions"][0]["state"], "default")

    def test_technical_qa_must_pass_and_bind_before_learning_or_promotion(self):
        contract, ledger = self.contract_and_ledger()
        for video_id, qa_status in (("VIDEO-01", "unavailable"), ("VIDEO-02", "fail")):
            fp, path = self.fingerprint(video_id, approved=True, technical_qa=qa_status)
            ledger = self.add(ledger, fp, path)
        recommendation = next(
            item
            for item in MODULE.build_learning_plan(contract, ledger)["promotion_recommendations"]
            if item["dimension_id"] == "DIM-ASPECT-RATIO"
        )
        self.assertFalse(recommendation["eligible"])
        self.assertEqual(recommendation["action"], "collect_more_approved_qa_evidence")
        self.assertEqual(recommendation["evidence_video_ids"], [])
        self.assertEqual(recommendation["qa_excluded_video_ids"], ["VIDEO-01", "VIDEO-02"])
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "not eligible"):
            MODULE.promote_dimension(contract, ledger, "DIM-ASPECT-RATIO")

    def test_technical_qa_is_canonical_in_ledger_and_cannot_be_forged(self):
        _, ledger = self.contract_and_ledger()
        fp, path = self.fingerprint("VIDEO-01", approved=True)
        ledger = self.add(ledger, fp, path)
        self.assertEqual(ledger["entries"][0]["technical_qa"], fp["technical_qa"])
        self.assertEqual(
            ledger["entries"][0]["approved_artifact_sha256"],
            fp["approval"]["approved_artifact_sha256"],
        )

        drifted = copy.deepcopy(ledger)
        drifted["entries"][0]["technical_qa"]["status"] = "fail"
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "disagrees"):
            MODULE.validate_ledger(drifted)

        forged = copy.deepcopy(fp)
        forged["technical_qa"]["artifact_sha256"] = "0" * 64
        forged["fingerprint_id"] = MODULE.expected_fingerprint_id(forged)
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "not bound"):
            MODULE.validate_fingerprint(forged)

    def test_extraction_uses_real_render_manifest_qa_bound_to_approved_artifact(self):
        project = self.root / "VIDEO-09"
        editable = project / "editable"
        editable.mkdir(parents=True)
        artifact = project / "approved.mp4"
        artifact.write_bytes(b"approved-video-09")
        artifact_sha = MODULE.file_sha256(artifact)
        (project / "manifest.json").write_text(json.dumps({
            "project_id": "series-test",
            "video_id": "VIDEO-09",
            "target": {"aspect_ratio": "9:16"},
        }), encoding="utf-8")
        render_path = editable / "manifest-render.json"
        render_path.write_text(json.dumps({
            "schema_version": "1.0.0",
            "video_id": "VIDEO-09",
            "status": "review_render_complete",
            "output": {"path": "../approved.mp4", "sha256": artifact_sha},
            "qa": {
                "hyperframes_check": "pass",
                "lint_errors": 0,
                "runtime_errors": 0,
                "layout_errors": 0,
            },
        }), encoding="utf-8")
        (editable / "index.html").write_text(
            '<div data-composition-id="scene-hook"></div>', encoding="utf-8"
        )
        receipt = self._approve("VIDEO-09", artifact)
        receipt_path = project / "approval.json"
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

        fingerprint = MODULE.extract_fingerprint(
            editable,
            approval_status="approved",
            approval_receipt=receipt_path,
            family_id="FAMILY-EDITORIAL-LOOP",
            archetype_id="ARCH-CONTRARIAN-LOOP",
        )
        self.assertEqual(fingerprint["technical_qa"]["status"], "pass")
        self.assertEqual(fingerprint["technical_qa"]["artifact_sha256"], artifact_sha)
        self.assertEqual(
            fingerprint["technical_qa"]["evidence_path"], MODULE._portable_path(render_path)
        )

        render = json.loads(render_path.read_text(encoding="utf-8"))
        render["output"]["sha256"] = "0" * 64
        render_path.write_text(json.dumps(render), encoding="utf-8")
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "does not match"):
            MODULE.extract_fingerprint(
                editable,
                approval_status="approved",
                approval_receipt=receipt_path,
                family_id="FAMILY-EDITORIAL-LOOP",
                archetype_id="ARCH-CONTRARIAN-LOOP",
            )

    def test_explicit_instruction_does_not_freeze_creative_class(self):
        contract, ledger = self.contract_and_ledger()
        promoted = MODULE.promote_dimension(
            contract, ledger, "DIM-NARRATIVE-ARCHETYPE", instruction_ref="USER-KEEP-ROTATING-001"
        )
        dimension = next(item for item in promoted["dimensions"] if item["dimension_id"] == "DIM-NARRATIVE-ARCHETYPE")
        self.assertEqual((dimension["state"], dimension["classification"], dimension["comparison"]), ("explicit", "rotating", "rotation"))

    def test_cross_series_evidence_cannot_promote(self):
        contract, _ = self.contract_and_ledger("series-alpha")
        _, ledger = self.contract_and_ledger("series-beta")
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "different series"):
            MODULE.build_learning_plan(contract, ledger)
        fp, path = self.fingerprint("VIDEO-01", series_id="series-alpha")
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "different series"):
            MODULE.add_fingerprint_to_ledger(ledger, fp, path)

    def test_approval_requires_live_bound_receipt_and_artifact(self):
        contract, ledger = self.contract_and_ledger()
        fp, path = self.fingerprint("VIDEO-01", approved=True)
        ledger = self.add(ledger, fp, path)
        (self.root / "VIDEO-01" / "approved.mp4").write_bytes(b"tampered")
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "approval|Approval"):
            MODULE.build_learning_plan(contract, ledger)

    def test_fingerprint_and_ledger_integrity_are_recomputed(self):
        _, ledger = self.contract_and_ledger()
        fp, path = self.fingerprint("VIDEO-01", approved=True)
        tampered = copy.deepcopy(fp)
        tampered["fields"]["technical.aspect_ratio"] = "4:5"
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "id/content mismatch"):
            MODULE.validate_fingerprint(tampered)
        clean_ledger = self.add(ledger, fp, path)
        ledger_with_duplicate_drift = copy.deepcopy(clean_ledger)
        ledger_with_duplicate_drift["entries"][0]["fields"]["technical.aspect_ratio"] = "4:5"
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "disagrees"):
            MODULE.validate_ledger(ledger_with_duplicate_drift)
        source = MODULE._path_from_stored(fp["source_files"][0]["path"])
        source.write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "source hash mismatch"):
            MODULE.validate_fingerprint(fp)
        path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "file hash"):
            MODULE.validate_ledger(clean_ledger)

    def test_family_archetype_and_lineage_are_validated(self):
        contract, ledger = self.contract_and_ledger()
        fp, _ = self.fingerprint("VIDEO-01", archetype="ARCH-CLAIM-PROOF-ACTION")
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "does not belong"):
            MODULE.check_fingerprint(contract, fp, ledger)
        cyclic = copy.deepcopy(contract)
        cyclic["template_families"][0]["lineage"]["parent_family_id"] = "FAMILY-CLEAN-AUTHORITY"
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "cycle"):
            MODULE.validate_contract(cyclic)

    def test_family_novelty_uses_declared_comparison_window(self):
        contract, ledger = self.contract_and_ledger()
        for video_id, palette in (("VIDEO-01", ["#111111"]), ("VIDEO-02", ["#222222"]), ("VIDEO-03", ["#333333"])):
            fp, path = self.fingerprint(video_id, approved=True, palette=palette)
            ledger = self.add(ledger, fp, path)
        candidate, _ = self.fingerprint("VIDEO-04", palette=["#111111"])
        one = copy.deepcopy(contract)
        one["template_families"][0]["novelty_budget"]["comparison_window"] = 1
        three = copy.deepcopy(contract)
        three["template_families"][0]["novelty_budget"]["comparison_window"] = 3
        novelty_one = MODULE.check_fingerprint(one, candidate, ledger)["variety"]["novelty_budget"]
        novelty_three = MODULE.check_fingerprint(three, candidate, ledger)["variety"]["novelty_budget"]
        self.assertEqual(novelty_one["status"], "within_budget")
        self.assertEqual(novelty_three["status"], "under_budget")
        self.assertEqual(novelty_three["predecessor_video_id"], "VIDEO-01")

    def test_first_recalibration_is_due_at_three_and_counts_never_go_negative(self):
        contract, ledger = self.contract_and_ledger()
        contract["recalibration_policy"]["interval_approved_videos"] = 5
        for video_id in ("VIDEO-01", "VIDEO-02", "VIDEO-03"):
            fp, path = self.fingerprint(video_id, approved=True)
            ledger = self.add(ledger, fp, path)
        plan = MODULE.build_learning_plan(contract, ledger)
        self.assertTrue(plan["recalibration"]["due"])
        self.assertEqual(plan["recalibration"]["approved_since_last_recalibration"], 3)
        contract["recalibration_policy"]["last_recalibrated_approved_count"] = 4
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "exceeds"):
            MODULE.build_learning_plan(contract, ledger)

    def test_paths_are_confined_symlink_free_and_outputs_do_not_overwrite_inputs(self):
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "traversal"):
            MODULE._path_from_stored("../outside.json")
        target = self.root / "target.json"
        target.write_text("{}", encoding="utf-8")
        link = self.root / "link.json"
        link.symlink_to(target)
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "Symlink"):
            MODULE.load_json(link)
        with self.assertRaisesRegex(MODULE.SeriesMemoryError, "overwrite"):
            MODULE._write_json(target, {}, protected_paths=(target,))


if __name__ == "__main__":
    unittest.main()
