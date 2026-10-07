#!/usr/bin/env python3

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


FRAMEWORK = Path(__file__).resolve().parents[2]
SCRIPTS = FRAMEWORK / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def load_module(name):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULE = load_module("build_publish_package")
RECEIPTS = load_module("approval_receipt")
MASTERS = load_module("check_master_profile")
SCHEMAS = load_module("schema_validation")
MASTER_TEMPLATE = FRAMEWORK / "templates/platform-master.json"
CATALOG_PATH = FRAMEWORK / "platforms/catalog.json"
CREATED_AT = "2020-01-01T10:00:00Z"
SOURCE_APPROVED_AT = "2020-01-01T11:00:00Z"
TONE_MAPPED_AT = "2020-01-01T12:00:00Z"
REVIEWED_AT = "2020-01-01T13:00:00Z"
SDR_APPROVED_AT = "2020-01-01T14:00:00Z"
LOCKED_AT = "2020-01-01T15:00:00Z"


def sdr_facts():
    return {
        "width": 1080,
        "height": 1920,
        "fps": 30.0,
        "aspect_ratio": "9:16",
        "orientation": "vertical",
        "duration_seconds": 60.0,
        "container": "mp4",
        "video_codec": "h264",
        "video_profile": "high",
        "pixel_format": "yuv420p",
        "video_bitrate_bps": 8_000_000,
        "color_primaries": "bt709",
        "color_transfer": "bt709",
        "color_space": "bt709",
        "audio_present": True,
        "audio_codec": "aac",
        "audio_profile": "lc",
        "audio_sample_rate_hz": 48000,
        "audio_channels": 2,
    }


def hdr_facts():
    value = sdr_facts()
    value.update(
        {
            "container": "mov",
            "video_codec": "hevc",
            "video_profile": "main 10",
            "pixel_format": "yuv420p10le",
            "video_bitrate_bps": 20_000_000,
            "color_primaries": "bt2020",
            "color_transfer": "arib-std-b67",
            "color_space": "bt2020nc",
        }
    )
    return value


def decision(decided_at, reference):
    return {
        "status": "approved",
        "explicit_user_approval": True,
        "approver": "owner",
        "decided_at": decided_at,
        "recorded_at": decided_at,
        "recorded_by": "codex",
        "evidence": {
            "kind": "user_message",
            "reference": reference,
            "excerpt": "Aprobado este archivo exacto.",
        },
        "scope": {"whole_artifact": True, "approved_layers": []},
    }


def approved_receipt(media, *, receipt_id, role, profile_id, decided_at, reference):
    receipt = RECEIPTS.prepare_receipt(
        media,
        receipt_id=receipt_id,
        project_id="PROJECT-EXAMPLE",
        video_id="VIDEO-01",
        media_role=role,
        profile_id=profile_id,
        created_at=CREATED_AT,
    )
    receipt["decision"] = decision(decided_at, reference)
    return RECEIPTS.seal_receipt(receipt, artifact_override=media)


def probe_evidence(media_hash, *, captured_at=CREATED_AT):
    return {
        "schema_version": "1.0.0",
        "kind": "ffprobe_capture",
        "authoritative": True,
        "media_sha256": media_hash,
        "captured_at": captured_at,
        "tool": "ffprobe-test",
    }


def loudness_evidence(media_hash):
    return {
        "schema_version": "1.0.0",
        "kind": "loudness_measurement",
        "authoritative": True,
        "media_sha256": media_hash,
        "measured_at": CREATED_AT,
        "tool": "ffmpeg-loudnorm-test",
    }


def tone_map_evidence(source_hash, output_hash):
    return {
        "schema_version": "1.0.0",
        "kind": "hdr_to_sdr_tone_map",
        "project_id": "PROJECT-EXAMPLE",
        "video_id": "VIDEO-01",
        "source_sha256": source_hash,
        "output_sha256": output_hash,
        "source_profile_id": "MASTER-PROFILE-EDITORIAL-HDR-001",
        "output_profile_id": "MASTER-PROFILE-SOCIAL-SDR-001",
        "tool": "ffmpeg",
        "tool_version": "test",
        "method": "bt2390",
        "parameters": "zscale=transfer=linear,tonemap=bt2390,zscale=bt709",
        "performed_at": TONE_MAPPED_AT,
    }


def visual_review(output_hash):
    return {
        "schema_version": "1.0.0",
        "kind": "hdr_to_sdr_visual_review",
        "project_id": "PROJECT-EXAMPLE",
        "video_id": "VIDEO-01",
        "output_sha256": output_hash,
        "profile_id": "MASTER-PROFILE-SOCIAL-SDR-001",
        "reviewer": "owner",
        "reviewed_at": REVIEWED_AT,
        "reference": "thread:test/turn:visual-review",
        "checks": {name: True for name in MASTERS.VISUAL_REVIEW_CHECKS},
        "note": "Revisión visual completa.",
    }


class PackageFixture:
    def __init__(self, directory, *, pending_master=False, catalog_path=CATALOG_PATH):
        self.root = Path(directory)
        self.catalog_path = Path(catalog_path)
        self.catalog = MODULE.load_catalog(self.catalog_path)
        self.master_media = self.root / "social-master.mp4"
        self.source_media = self.root / "editorial-master.mov"
        self.master_media.write_bytes(b"approved-sdr-master")
        self.source_media.write_bytes(b"approved-editorial-master")

        self.source_receipt = approved_receipt(
            self.source_media,
            receipt_id="APPROVAL-VIDEO-01-HDR",
            role="editorial_mezzanine",
            profile_id="MASTER-PROFILE-EDITORIAL-HDR-001",
            decided_at=SOURCE_APPROVED_AT,
            reference="thread:test/turn:hdr-approval",
        )
        self.source_receipt_path = self.root / "editorial-approval.json"
        self._write(self.source_receipt_path, self.source_receipt)

        source_hash = self.source_receipt["artifact"]["sha256"]
        output_hash = RECEIPTS.sha256_file(self.master_media)
        self.report = MASTERS.evaluate_profile(
            MASTERS.load_profile(MODULE.SOCIAL_PROFILE_PATH),
            sdr_facts(),
            media_path=self.master_media.resolve(),
            media_sha256=output_hash,
            probe_authoritative=True,
            probe_evidence=probe_evidence(output_hash),
            loudness={"integrated_lufs": -14.0, "true_peak_dbtp": -1.1},
            loudness_authoritative=True,
            loudness_evidence=loudness_evidence(output_hash),
            approval_receipt=self.source_receipt,
            approval_receipt_path=self.source_receipt_path,
            source_master=self.source_media.resolve(),
            source_profile=MASTERS.load_profile(MODULE.EDITORIAL_PROFILE_PATH),
            source_metadata=hdr_facts(),
            source_probe_authoritative=True,
            source_probe_evidence=probe_evidence(source_hash),
            expected_project_id="PROJECT-EXAMPLE",
            expected_video_id="VIDEO-01",
            tone_map_evidence=tone_map_evidence(source_hash, output_hash),
            visual_review=visual_review(output_hash),
        )
        self.report_path = self.root / "master-profile-report.json"
        self._write(self.report_path, self.report)

        self.receipt = approved_receipt(
            self.master_media,
            receipt_id="APPROVAL-VIDEO-01-SDR",
            role="social_delivery_master",
            profile_id="MASTER-PROFILE-SOCIAL-SDR-001",
            decided_at=SDR_APPROVED_AT,
            reference="thread:test/turn:sdr-approval",
        )
        self.receipt_path = self.root / "sdr-approval.json"
        self._write(self.receipt_path, self.receipt)

        self.project = self.root / "editable"
        self.project.mkdir()
        (self.project / "index.html").write_text("<main>approved edit</main>", encoding="utf-8")
        self.cut_plan = self.root / "cut-plan.json"
        self.cut_plan.write_text('{"cuts":[1,2,3]}\n', encoding="utf-8")
        self.audio_mix = self.root / "audio-mix.wav"
        self.audio_mix.write_bytes(b"approved-audio-mix")

        self.master = json.loads(MASTER_TEMPLATE.read_text(encoding="utf-8"))
        self.master["project_path"] = "editable"
        self.master["approval"] = {
            "status": "pending" if pending_master else "approved",
            "explicit_user_approval": not pending_master,
            "approved_by": None if pending_master else "owner",
            "approved_at": None if pending_master else SDR_APPROVED_AT,
            "note": "Pendiente." if pending_master else "Master social aprobado.",
        }
        project_fingerprint = MODULE.fingerprint_content_artifact(self.project)
        cut_fingerprint = MODULE.fingerprint_content_artifact(self.cut_plan)
        audio_fingerprint = MODULE.fingerprint_content_artifact(self.audio_mix)
        self.master["content_lock"] = {
            "status": "unlocked" if pending_master else "locked",
            "locked_at": None if pending_master else LOCKED_AT,
            "take": not pending_master,
            "cuts": not pending_master,
            "voice": not pending_master,
            "semantics": not pending_master,
            "assets": not pending_master,
        }
        self.master["hashes"] = {
            "project_sha256": None if pending_master else project_fingerprint["sha256"],
            "cut_plan_sha256": None if pending_master else cut_fingerprint["sha256"],
            "audio_mix_sha256": None if pending_master else audio_fingerprint["sha256"],
        }
        self.master_path = self.root / "platform-master.json"
        self._write(self.master_path, self.master)

        if pending_master:
            self.lock = {
                "schema_version": "1.0.0",
                "lock_id": "CONTENT-LOCK-VIDEO-01-PENDING",
                "project_id": "PROJECT-EXAMPLE",
                "video_id": "VIDEO-01",
                "status": "pending",
                "platform_master_sha256": None,
                "hash_strategy": "file-sha256-or-directory-tree-sha256-v1",
                "locked_at": None,
                "artifacts": [],
                "binding": {
                    "algorithm": "sha256",
                    "canonicalization": "json-sort-keys-utf8-v1",
                    "payload_sha256": None,
                },
                "created_at": LOCKED_AT,
            }
        else:
            self.lock = MODULE.seal_content_lock_evidence(
                {
                    "schema_version": "1.0.0",
                    "lock_id": "CONTENT-LOCK-VIDEO-01-V1",
                    "project_id": "PROJECT-EXAMPLE",
                    "video_id": "VIDEO-01",
                    "status": "sealed",
                    "platform_master_sha256": RECEIPTS.sha256_file(self.master_path),
                    "hash_strategy": "file-sha256-or-directory-tree-sha256-v1",
                    "locked_at": LOCKED_AT,
                    "artifacts": [
                        {"role": "project", "path": "editable", **project_fingerprint},
                        {"role": "cut_plan", "path": "cut-plan.json", **cut_fingerprint},
                        {"role": "audio_mix", "path": "audio-mix.wav", **audio_fingerprint},
                    ],
                    "binding": {
                        "algorithm": "sha256",
                        "canonicalization": "json-sort-keys-utf8-v1",
                        "payload_sha256": None,
                    },
                    "created_at": LOCKED_AT,
                }
            )
        self.lock_path = self.root / "content-lock-evidence.json"
        self._write(self.lock_path, self.lock)

    @staticmethod
    def _write(path, value):
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def reseal_lock(self):
        self._write(self.master_path, self.master)
        if self.lock["status"] == "sealed":
            self.lock["platform_master_sha256"] = RECEIPTS.sha256_file(self.master_path)
            self.lock = MODULE.seal_content_lock_evidence(self.lock)
        self._write(self.lock_path, self.lock)

    def arguments(self, **overrides):
        values = {
            "master": self.master,
            "master_manifest_path": self.master_path,
            "master_media": self.master_media,
            "receipt": self.receipt,
            "receipt_path": self.receipt_path,
            "source_approval_receipt": self.source_receipt,
            "source_approval_receipt_path": self.source_receipt_path,
            "master_profile_report": self.report,
            "master_profile_report_path": self.report_path,
            "content_lock_evidence": self.lock,
            "content_lock_evidence_path": self.lock_path,
            "catalog": self.catalog,
            "catalog_path": self.catalog_path,
            "output_dir": "deliveries",
        }
        values.update(overrides)
        return values

    def build(self, **overrides):
        probe_values = overrides.pop("_probe_values", [sdr_facts(), hdr_facts()])
        values = self.arguments(**overrides)
        with mock.patch.object(MODULE, "_probe_media", side_effect=probe_values):
            return MODULE.build_package(**values)

    def materialize(self, package, adaptation, out, *, force=False):
        with mock.patch.object(
            MODULE, "_probe_media", side_effect=[sdr_facts(), hdr_facts()]
        ):
            return MODULE.materialize(package, adaptation, out, force=force)


class PublishPackageTests(unittest.TestCase):
    def test_verified_inputs_build_instagram_default_with_full_gates(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            package, adaptation = fixture.build()
            self.assertEqual(package["status"], "ready_for_derivative_build")
            self.assertEqual(adaptation["status"], "ready_for_platform_preview")
            self.assertEqual(len(package["targets"]), 1)
            self.assertEqual(package["targets"][0]["platform"], "instagram")
            briefs = [target["brief_output"] for target in package["targets"]]
            self.assertEqual(len(briefs), len(set(briefs)))
            for target in package["targets"]:
                self.assertIn("semantic_match", target["required_gates"])
                self.assertIn("content_lock", target["required_gates"])
                self.assertEqual(
                    target["provenance"]["catalog_sha256"],
                    RECEIPTS.sha256_file(CATALOG_PATH),
                )
            self.assertEqual(
                package["adaptation"]["catalog_path"], str(CATALOG_PATH.resolve())
            )
            self.assertEqual(
                package["source"]["platform_manifest_sha256"],
                RECEIPTS.sha256_file(fixture.master_path),
            )
            self.assertEqual(
                package["source"]["content_lock_evidence_sha256"],
                RECEIPTS.sha256_file(fixture.lock_path),
            )
            self.assertFalse(package["governance"]["cryptographic_identity_established"])
            self.assertEqual(
                package["governance"]["ready_scope"], "derivative_build_only"
            )
            self.assertFalse(package["governance"]["publication_ready"])
            for target in package["targets"]:
                human_gate = {
                    gate["id"]: gate for gate in target["gates"]
                }["human_publication_approval"]
                self.assertEqual(human_gate["status"], "pending")
                self.assertIsNone(human_gate["evidence"])
            schema = SCHEMAS.load_json(FRAMEWORK / "schemas/publish-package.schema.json")
            self.assertEqual(SCHEMAS.validate_document(package, schema), [])

    def test_minimal_forged_profile_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            forged = {
                "profile_id": MODULE.SOCIAL_PROFILE,
                "media_sha256": fixture.receipt["artifact"]["sha256"],
                "publication_ready": True,
            }
            fixture.report = forged
            fixture._write(fixture.report_path, forged)
            with self.assertRaisesRegex(MODULE.PublishPackageError, "fields must be exactly"):
                fixture.build()

    def test_tampered_complete_profile_report_fails_fresh_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            fixture.report["loudness"]["integrated_lufs"] = -5.0
            fixture._write(fixture.report_path, fixture.report)
            with self.assertRaisesRegex(MODULE.PublishPackageError, "fresh replay"):
                fixture.build()

    def test_forged_editorial_probe_metadata_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            fixture.report["source_profile_verification"]["metadata"]["color_space"] = "bt709"
            fixture._write(fixture.report_path, fixture.report)
            with self.assertRaisesRegex(
                MODULE.PublishPackageError, "fresh editorial media probe"
            ):
                fixture.build()

    def test_report_object_must_equal_its_file(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            supplied = copy.deepcopy(fixture.report)
            supplied["status_notice"] = "different"
            with self.assertRaisesRegex(MODULE.PublishPackageError, "differs from its declared file"):
                fixture.build(master_profile_report=supplied)

    def test_catalog_file_is_bound_and_recorded_not_defaulted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            custom_path = root / "custom-catalog.json"
            custom_path.write_text(CATALOG_PATH.read_text(encoding="utf-8"), encoding="utf-8")
            fixture = PackageFixture(root, catalog_path=custom_path)
            package, adaptation = fixture.build()
            self.assertEqual(package["adaptation"]["catalog_path"], str(custom_path.resolve()))
            self.assertEqual(adaptation["catalog"]["path"], str(custom_path.resolve()))
            altered = copy.deepcopy(fixture.catalog)
            altered["updated_at"] = "2020-01-01"
            with self.assertRaisesRegex(MODULE.PublishPackageError, "differs from its declared file"):
                fixture.build(catalog=altered)

    def test_changed_locked_project_invalidates_package(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            (fixture.project / "index.html").write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(MODULE.PublishPackageError, "does not match the artifact"):
                fixture.build()

    def test_dummy_master_content_hash_is_rejected_even_if_lock_is_resealed(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            fixture.master["hashes"]["cut_plan_sha256"] = "a" * 64
            fixture.reseal_lock()
            with self.assertRaisesRegex(MODULE.PublishPackageError, "is not the real artifact hash"):
                fixture.build()

    def test_changed_master_media_invalidates_approval_before_packaging(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            fixture.master_media.write_bytes(b"changed-after-approval")
            with self.assertRaisesRegex(MODULE.PublishPackageError, "receipt failed"):
                fixture.build()

    def test_source_receipt_object_must_equal_its_file(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            supplied = copy.deepcopy(fixture.source_receipt)
            supplied["notes"] = "tampered"
            with self.assertRaisesRegex(MODULE.PublishPackageError, "differs from its declared file"):
                fixture.build(source_approval_receipt=supplied)

    def test_sdr_receipt_object_must_equal_its_file(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            supplied = copy.deepcopy(fixture.receipt)
            supplied["notes"] = "tampered"
            with self.assertRaisesRegex(MODULE.PublishPackageError, "differs from its declared file"):
                fixture.build(receipt=supplied)

    def test_input_and_output_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            media_link = fixture.root / "master-link.mp4"
            media_link.symlink_to(fixture.master_media)
            with self.assertRaisesRegex(MODULE.PublishPackageError, "symlink"):
                fixture.build(master_media=media_link)

            parent_link = fixture.root / "linked-parent"
            parent_link.symlink_to(fixture.root, target_is_directory=True)
            with self.assertRaisesRegex(MODULE.PublishPackageError, "symlink"):
                fixture.build(master_profile_report_path=parent_link / fixture.report_path.name)

            package, adaptation = fixture.build()
            real_out = fixture.root / "real-output"
            real_out.mkdir()
            output_link = fixture.root / "output-link"
            output_link.symlink_to(real_out, target_is_directory=True)
            with self.assertRaisesRegex(MODULE.PublishPackageError, "symlink"):
                fixture.materialize(package, adaptation, output_link)

            nested_out = fixture.root / "nested-output"
            nested_out.mkdir()
            victim = fixture.root / "victim"
            victim.mkdir()
            (nested_out / "instagram").symlink_to(victim, target_is_directory=True)
            with self.assertRaisesRegex(MODULE.PublishPackageError, "symlink"):
                fixture.materialize(package, adaptation, nested_out)

    def test_symlink_inside_locked_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            (fixture.project / "linked.txt").symlink_to(fixture.cut_plan)
            with self.assertRaisesRegex(MODULE.PublishPackageError, "contains a symlink"):
                fixture.build()

    def test_invalid_numeric_media_fact_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            malformed = sdr_facts()
            malformed["fps"] = {"not": "numeric"}
            with self.assertRaisesRegex(MODULE.PublishPackageError, "does not match"):
                fixture.build(_probe_values=[malformed, hdr_facts()])

    def test_malformed_master_is_wrapped_as_publish_error(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            malformed = copy.deepcopy(fixture.master)
            malformed.pop("technical")
            fixture._write(fixture.master_path, malformed)
            with self.assertRaisesRegex(MODULE.PublishPackageError, "invalid platform master"):
                fixture.build(master=malformed)

    def test_pending_master_remains_blocked_with_pending_lock_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory, pending_master=True)
            package, _ = fixture.build()
            self.assertEqual(package["status"], "blocked")
            self.assertTrue(package["blocking_reasons"])

    def test_materialization_is_explicit_atomic_and_requires_force(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            package, adaptation = fixture.build()
            out = fixture.root / "package"
            self.assertFalse(out.exists())
            fixture.materialize(package, adaptation, out)
            self.assertTrue((out / "publish-package.json").is_file())
            self.assertTrue((out / "platform-adaptation.json").is_file())
            for target in package["targets"]:
                self.assertTrue((out / target["brief_output"]).is_file())
            with self.assertRaisesRegex(MODULE.PublishPackageError, "without --force"):
                fixture.materialize(package, adaptation, out)
            fixture.materialize(package, adaptation, out, force=True)

    def test_force_never_replaces_an_arbitrary_or_provenance_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            package, adaptation = fixture.build()
            arbitrary = fixture.root / "not-a-package"
            arbitrary.mkdir()
            sentinel = arbitrary / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(
                MODULE.PublishPackageError, "existing publish package"
            ):
                fixture.materialize(package, adaptation, arbitrary, force=True)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")

            with self.assertRaisesRegex(
                MODULE.PublishPackageError, "provenance input"
            ):
                fixture.materialize(package, adaptation, fixture.root, force=True)

            with self.assertRaisesRegex(
                MODULE.PublishPackageError, "overlaps content-lock project"
            ):
                fixture.materialize(
                    package, adaptation, fixture.project / "nested-package"
                )

    def test_materialize_rejects_dotdot_even_when_adaptation_is_resealed(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            package, adaptation = fixture.build()
            forged = copy.deepcopy(adaptation)
            forged["output_root"] = "deliveries/../escape"
            forged = MODULE.seal_document(forged)
            with self.assertRaisesRegex(MODULE.PublishPackageError, r"\. or \.\."):
                fixture.materialize(package, forged, fixture.root / "package")

    def test_materialize_rejects_resealed_forged_package_semantics(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            package, adaptation = fixture.build()
            forged = copy.deepcopy(package)
            forged["adaptation"]["target_count"] += 1
            forged = MODULE.seal_document(forged)
            with self.assertRaisesRegex(MODULE.PublishPackageError, "summary is inconsistent"):
                fixture.materialize(forged, adaptation, fixture.root / "package")

    def test_content_fingerprint_fails_on_unreadable_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "locked"
            root.mkdir()
            (root / "file.txt").write_text("locked", encoding="utf-8")
            real_scandir = MODULE.os.scandir

            def guarded(path):
                if Path(path).resolve() == root.resolve():
                    raise PermissionError("denied by test")
                return real_scandir(path)

            with mock.patch.object(MODULE.os, "scandir", side_effect=guarded):
                with self.assertRaisesRegex(MODULE.PublishPackageError, "cannot be read completely"):
                    MODULE.fingerprint_content_artifact(root)

    def test_non_video_bytes_cannot_use_a_productive_probe_bypass(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            self.assertNotIn("media_facts", fixture.arguments())
            with self.assertRaisesRegex(MODULE.PublishPackageError, "ffprobe failed"):
                MODULE.build_package(**fixture.arguments())

    def test_additional_profile_gate_is_preserved_and_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = MODULE.load_catalog(CATALOG_PATH)
            catalog = copy.deepcopy(catalog)
            catalog["profiles"][1]["adaptation_policy"]["required_gates"].append(
                "brand_legal_review"
            )
            catalog_path = root / "catalog-extra-gate.json"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            fixture = PackageFixture(root, catalog_path=catalog_path)
            target_id = catalog["profiles"][1]["id"]
            package, adaptation = fixture.build(target_ids=[target_id])
            adaptation_gate = {
                item["id"]: item for item in adaptation["targets"][0]["gates"]
            }["brand_legal_review"]
            package_gate = {
                item["id"]: item for item in package["targets"][0]["gates"]
            }["brand_legal_review"]
            self.assertEqual(adaptation_gate["status"], "pending")
            self.assertEqual(package_gate["status"], "pending")
            self.assertIn("brand_legal_review", package["targets"][0]["required_gates"])

    def test_failed_staging_never_exposes_partial_package(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            package, adaptation = fixture.build()
            out = fixture.root / "atomic-package"
            real_write = MODULE._write_staged_document
            calls = {"count": 0}

            def fail_second(path, value):
                calls["count"] += 1
                if calls["count"] == 2:
                    raise OSError("simulated disk failure")
                return real_write(path, value)

            with mock.patch.object(MODULE, "_write_staged_document", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "simulated disk failure"):
                    fixture.materialize(package, adaptation, out)
            self.assertFalse(out.exists())
            self.assertEqual(list(fixture.root.glob(".atomic-package.stage-*")), [])

    def test_source_change_during_staging_aborts_before_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            package, adaptation = fixture.build()
            out = fixture.root / "snapshot-package"
            real_write = MODULE._write_staged_document
            changed = {"done": False}

            def mutate_source(path, value):
                result = real_write(path, value)
                if not changed["done"]:
                    fixture.master_media.write_bytes(b"changed-during-stage")
                    changed["done"] = True
                return result

            with mock.patch.object(MODULE, "_write_staged_document", side_effect=mutate_source):
                with self.assertRaisesRegex(MODULE.PublishPackageError, "changed before atomic commit"):
                    fixture.materialize(package, adaptation, out)
            self.assertFalse(out.exists())

    def test_locked_project_change_during_staging_aborts_before_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            package, adaptation = fixture.build()
            out = fixture.root / "locked-snapshot-package"
            real_write = MODULE._write_staged_document
            changed = {"done": False}

            def mutate_locked_project(path, value):
                result = real_write(path, value)
                if not changed["done"]:
                    (fixture.project / "late-change.txt").write_text(
                        "changed during staging", encoding="utf-8"
                    )
                    changed["done"] = True
                return result

            with mock.patch.object(
                MODULE, "_write_staged_document", side_effect=mutate_locked_project
            ):
                with self.assertRaisesRegex(
                    MODULE.PublishPackageError, "changed before atomic commit"
                ):
                    fixture.materialize(package, adaptation, out)
            self.assertFalse(out.exists())

    def test_package_id_binds_catalog_targets_lock_and_report(self):
        source = {
            "sha256": "a" * 64,
            "platform_manifest_sha256": "b" * 64,
            "approval_receipt_sha256": "c" * 64,
            "master_profile_report_sha256": "d" * 64,
            "source_approval_receipt_sha256": "e" * 64,
            "content_lock_evidence_sha256": "f" * 64,
        }
        baseline = MODULE._package_id(
            "VIDEO-01", source=source, catalog_sha256="1" * 64,
            target_profile_ids=["PLATFORM-A-001"],
        )
        variants = []
        for field in ("master_profile_report_sha256", "content_lock_evidence_sha256"):
            changed = dict(source)
            changed[field] = "0" * 64
            variants.append(
                MODULE._package_id(
                    "VIDEO-01", source=changed, catalog_sha256="1" * 64,
                    target_profile_ids=["PLATFORM-A-001"],
                )
            )
        variants.extend(
            [
                MODULE._package_id(
                    "VIDEO-01", source=source, catalog_sha256="2" * 64,
                    target_profile_ids=["PLATFORM-A-001"],
                ),
                MODULE._package_id(
                    "VIDEO-01", source=source, catalog_sha256="1" * 64,
                    target_profile_ids=["PLATFORM-B-001"],
                ),
            ]
        )
        self.assertTrue(all(value != baseline for value in variants))

    def test_written_documents_have_valid_final_seals(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = PackageFixture(directory)
            package, adaptation = fixture.build()
            out = fixture.materialize(package, adaptation, fixture.root / "sealed-package")
            MODULE.verify_document_binding(
                json.loads((out / "publish-package.json").read_text(encoding="utf-8")),
                "publish package",
            )
            MODULE.verify_document_binding(
                json.loads((out / "platform-adaptation.json").read_text(encoding="utf-8")),
                "platform adaptation",
            )
            for target in package["targets"]:
                MODULE.verify_document_binding(
                    json.loads((out / target["brief_output"]).read_text(encoding="utf-8")),
                    "package brief",
                )

    def test_templates_match_schemas_and_are_fail_closed(self):
        for name in ("publish-package", "content-lock-evidence"):
            with self.subTest(name=name):
                template = json.loads(
                    (FRAMEWORK / "templates" / f"{name}.json").read_text(encoding="utf-8")
                )
                schema = SCHEMAS.load_json(FRAMEWORK / "schemas" / f"{name}.schema.json")
                self.assertEqual(SCHEMAS.validate_document(template, schema), [])
        package_template = json.loads(
            (FRAMEWORK / "templates/publish-package.json").read_text(encoding="utf-8")
        )
        lock_template = json.loads(
            (FRAMEWORK / "templates/content-lock-evidence.json").read_text(encoding="utf-8")
        )
        self.assertEqual(package_template["status"], "blocked")
        self.assertFalse(package_template["governance"]["auto_publish"])
        self.assertEqual(lock_template["status"], "pending")
        self.assertIsNone(lock_template["binding"]["payload_sha256"])


if __name__ == "__main__":
    unittest.main()
