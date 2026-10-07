#!/usr/bin/env python3

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path


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


RECEIPTS = load_module("approval_receipt")
MASTERS = load_module("check_master_profile")
SCHEMAS = load_module("schema_validation")
CREATED_AT = "2020-01-01T10:00:00Z"
DECIDED_AT = "2020-01-01T11:00:00Z"
RECORDED_AT = "2020-01-01T12:00:00Z"
TONE_MAPPED_AT = "2020-01-01T12:00:00Z"
REVIEWED_AT = "2020-01-01T13:00:00Z"


def probe_hdr(duration="20.0"):
    return {
        "streams": [
            {
                "codec_type": "video",
                "codec_name": "hevc",
                "profile": "Main 10",
                "width": 1080,
                "height": 1920,
                "pix_fmt": "yuv420p10le",
                "avg_frame_rate": "30/1",
                "duration": duration,
                "bit_rate": "20000000",
                "color_primaries": "bt2020",
                "color_transfer": "arib-std-b67",
                "color_space": "bt2020nc",
            },
            {
                "codec_type": "audio",
                "codec_name": "aac",
                "profile": "LC",
                "sample_rate": "48000",
                "channels": 2,
            },
        ],
        "format": {
            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            "duration": duration,
            "bit_rate": "20500000",
        },
    }


def probe_sdr(duration="20.0"):
    value = probe_hdr(duration)
    value["streams"][0].update(
        {
            "codec_name": "h264",
            "profile": "High",
            "pix_fmt": "yuv420p",
            "bit_rate": "8000000",
            "color_primaries": "bt709",
            "color_transfer": "bt709",
            "color_space": "bt709",
        }
    )
    value["format"]["bit_rate"] = "8200000"
    return value


def approval_decision(
    *,
    decided_at=DECIDED_AT,
    recorded_at=RECORDED_AT,
    whole_artifact=True,
    approved_layers=None,
):
    return {
        "status": "approved",
        "explicit_user_approval": True,
        "approver": "owner",
        "decided_at": decided_at,
        "recorded_at": recorded_at,
        "recorded_by": "codex",
        "evidence": {
            "kind": "user_message",
            "reference": "thread:test/turn:1",
            "excerpt": "Aprobado este archivo exacto.",
        },
        "scope": {
            "whole_artifact": whole_artifact,
            "approved_layers": approved_layers or [],
        },
    }


def approve(receipt, artifact):
    value = copy.deepcopy(receipt)
    value["decision"] = approval_decision()
    return RECEIPTS.seal_receipt(value, artifact_override=artifact)


def tone_map_evidence(project_id, video_id, source_hash, output_hash, source_profile_id, output_profile_id):
    return {
        "schema_version": "1.0.0",
        "kind": "hdr_to_sdr_tone_map",
        "project_id": project_id,
        "video_id": video_id,
        "source_sha256": source_hash,
        "output_sha256": output_hash,
        "source_profile_id": source_profile_id,
        "output_profile_id": output_profile_id,
        "tool": "ffmpeg",
        "tool_version": "test",
        "method": "bt2390",
        "parameters": "zscale=transfer=linear,tonemap=bt2390,zscale=bt709",
        "performed_at": TONE_MAPPED_AT,
    }


def visual_review(project_id, video_id, output_hash, profile_id):
    return {
        "schema_version": "1.0.0",
        "kind": "hdr_to_sdr_visual_review",
        "project_id": project_id,
        "video_id": video_id,
        "output_sha256": output_hash,
        "profile_id": profile_id,
        "reviewer": "owner",
        "reviewed_at": REVIEWED_AT,
        "reference": "thread:test/turn:review",
        "checks": {name: True for name in MASTERS.VISUAL_REVIEW_CHECKS},
        "note": "Revisión visual completa.",
    }


def probe_evidence(probe, media_hash, authoritative=True):
    return {
        "schema_version": "1.0.0",
        "kind": "ffprobe_capture" if authoritative else "ffprobe_fixture",
        "authoritative": authoritative,
        "media_sha256": media_hash if authoritative else None,
        "captured_at": CREATED_AT if authoritative else None,
        "tool": "ffprobe-test",
        "probe": probe,
    }


def loudness_evidence(media_hash, authoritative=True):
    return {
        "schema_version": "1.0.0",
        "kind": "loudness_measurement" if authoritative else "loudness_fixture",
        "authoritative": authoritative,
        "media_sha256": media_hash if authoritative else None,
        "measured_at": CREATED_AT if authoritative else None,
        "tool": "ffmpeg-loudnorm-test",
        "measurement": {"integrated_lufs": -14.0, "true_peak_dbtp": -1.1},
    }


class ApprovalReceiptTests(unittest.TestCase):
    def test_template_matches_schema_but_does_not_claim_approval(self):
        template = json.loads((FRAMEWORK / "templates/approval-receipt.json").read_text(encoding="utf-8"))
        schema = json.loads((FRAMEWORK / "schemas/approval-receipt.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(SCHEMAS.validate_document(template, schema), [])
        self.assertEqual(template["decision"]["status"], "pending")
        self.assertFalse(template["decision"]["explicit_user_approval"])
        self.assertIsNone(template["decision"]["recorded_at"])
        self.assertIsNone(template["artifact"]["sha256"])

    def test_prepare_binds_exact_hash_but_stays_pending(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "video.mov"
            artifact.write_bytes(b"editorial-master")
            receipt = RECEIPTS.prepare_receipt(
                artifact,
                receipt_id="APPROVAL-VIDEO-01-V2",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                profile_id="MASTER-PROFILE-EDITORIAL-HDR-001",
                created_at=CREATED_AT,
            )
            report = RECEIPTS.verify_receipt(receipt, artifact_override=artifact)
            self.assertEqual(report["overall_status"], "valid_pending")
            self.assertEqual(report["artifact_status"], "match")
            self.assertEqual(report["binding_status"], "match")
            self.assertFalse(report["usable_as_approval"])
            self.assertEqual(
                receipt["artifact"]["profile_id"],
                "MASTER-PROFILE-EDITORIAL-HDR-001",
            )
            self.assertEqual(
                RECEIPTS.canonical_payload(receipt)["artifact"]["profile_id"],
                "MASTER-PROFILE-EDITORIAL-HDR-001",
            )

    def test_changed_artifact_invalidates_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "video.mov"
            artifact.write_bytes(b"version-one")
            receipt = RECEIPTS.prepare_receipt(
                artifact,
                receipt_id="APPROVAL-VIDEO-01-V2",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            artifact.write_bytes(b"version-two")
            report = RECEIPTS.verify_receipt(receipt, artifact_override=artifact)
            self.assertEqual(report["overall_status"], "invalid")
            self.assertIn(report["artifact_status"], {"hash_mismatch", "hash_and_size_mismatch"})

    def test_payload_edit_after_sealing_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "video.mov"
            artifact.write_bytes(b"master")
            receipt = RECEIPTS.prepare_receipt(
                artifact,
                receipt_id="APPROVAL-VIDEO-01-V2",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            receipt["notes"] = "edited after sealing"
            report = RECEIPTS.verify_receipt(receipt, artifact_override=artifact)
            self.assertEqual(report["binding_status"], "mismatch")
            self.assertEqual(report["overall_status"], "invalid")

    def test_approved_status_requires_evidence_and_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "video.mov"
            artifact.write_bytes(b"master")
            receipt = RECEIPTS.prepare_receipt(
                artifact,
                receipt_id="APPROVAL-VIDEO-01-V2",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            receipt["decision"]["status"] = "approved"
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "explicit_user_approval"):
                RECEIPTS.seal_receipt(receipt, artifact_override=artifact)

    def test_explicit_evidenced_approval_verifies(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "video.mov"
            artifact.write_bytes(b"approved-master")
            pending = RECEIPTS.prepare_receipt(
                artifact,
                receipt_id="APPROVAL-VIDEO-01-V2",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            receipt = approve(pending, artifact)
            report = RECEIPTS.verify_receipt(receipt, artifact_override=artifact)
            self.assertEqual(report["overall_status"], "approved_match")
            self.assertTrue(report["usable_as_approval"])

    def test_cli_refuses_output_without_explicit_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "video.mov"
            output = root / "receipt.json"
            artifact.write_bytes(b"master")
            args = [
                "prepare",
                "--artifact",
                str(artifact),
                "--receipt-id",
                "APPROVAL-VIDEO-01-V2",
                "--project-id",
                "SERIE-TEST",
                "--video-id",
                "VIDEO-01",
                "--created-at",
                CREATED_AT,
                "--out",
                str(output),
            ]
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                code = RECEIPTS.main(args)
            self.assertEqual(code, 2)
            self.assertFalse(output.exists())

    def test_seal_refuses_artifact_rebind_even_when_new_hash_and_size_are_supplied(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "original.mov"
            replacement = root / "replacement.mov"
            original.write_bytes(b"original")
            replacement.write_bytes(b"replacement")
            receipt = RECEIPTS.prepare_receipt(
                original,
                receipt_id="APPROVAL-VIDEO-01-REBIND",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            candidate = copy.deepcopy(receipt)
            candidate["artifact"].update(
                path=str(replacement.resolve()),
                sha256=RECEIPTS.sha256_file(replacement),
                size_bytes=replacement.stat().st_size,
            )
            candidate["decision"] = approval_decision()
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "only decision fields"):
                RECEIPTS.seal_receipt(candidate, artifact_override=replacement)

    def test_seal_refuses_nondecision_edit_and_second_decision_transition(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "video.mov"
            artifact.write_bytes(b"master")
            pending = RECEIPTS.prepare_receipt(
                artifact,
                receipt_id="APPROVAL-VIDEO-01-IMMUTABLE",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            edited = copy.deepcopy(pending)
            edited["notes"] = "changed together with approval"
            edited["decision"] = approval_decision()
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "only decision fields"):
                RECEIPTS.seal_receipt(edited, artifact_override=artifact)

            sealed = approve(pending, artifact)
            sealed["decision"] = approval_decision(decided_at="2020-01-01T11:30:00Z")
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "only decision fields"):
                RECEIPTS.seal_receipt(sealed, artifact_override=artifact)

    def test_receipt_supports_retrospective_approval_but_enforces_recording_chronology(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "video.mov"
            artifact.write_bytes(b"master")
            pending = RECEIPTS.prepare_receipt(
                artifact,
                receipt_id="APPROVAL-VIDEO-01-TIME",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            retrospective = copy.deepcopy(pending)
            retrospective["decision"] = approval_decision(
                decided_at="2019-12-31T23:59:59Z",
                recorded_at=RECORDED_AT,
            )
            retrospective = RECEIPTS.seal_receipt(retrospective, artifact_override=artifact)
            self.assertEqual(
                RECEIPTS.verify_receipt(retrospective, artifact_override=artifact)["overall_status"],
                "approved_match",
            )

            decision_after_record = copy.deepcopy(pending)
            decision_after_record["decision"] = approval_decision(
                decided_at="2020-01-01T13:00:00Z",
                recorded_at=RECORDED_AT,
            )
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "decided_at cannot follow"):
                RECEIPTS.seal_receipt(decision_after_record, artifact_override=artifact)

            prepared_after_record = RECEIPTS.prepare_receipt(
                artifact,
                receipt_id="APPROVAL-VIDEO-01-LATE-PREPARE",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at="2020-01-01T13:00:00Z",
            )
            prepared_after_record["decision"] = approval_decision(recorded_at=RECORDED_AT)
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "created_at cannot follow"):
                RECEIPTS.seal_receipt(prepared_after_record, artifact_override=artifact)

            future_decision = copy.deepcopy(pending)
            future_decision["decision"] = approval_decision(
                decided_at="2999-01-01T00:00:00Z",
                recorded_at=RECORDED_AT,
            )
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "decided_at cannot be in the future"):
                RECEIPTS.seal_receipt(future_decision, artifact_override=artifact)

            future_record = copy.deepcopy(pending)
            future_record["decision"] = approval_decision(
                decided_at=DECIDED_AT,
                recorded_at="2999-01-01T00:01:00Z",
            )
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "recorded_at cannot be in the future"):
                RECEIPTS.seal_receipt(future_record, artifact_override=artifact)

            missing_record = copy.deepcopy(pending)
            missing_record["decision"] = approval_decision()
            missing_record["decision"].pop("recorded_at")
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "recorded_at"):
                RECEIPTS.seal_receipt(missing_record, artifact_override=artifact)

            malformed_record = copy.deepcopy(pending)
            malformed_record["decision"] = approval_decision(recorded_at="not-rfc3339")
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "RFC 3339"):
                RECEIPTS.seal_receipt(malformed_record, artifact_override=artifact)

            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "future"):
                RECEIPTS.prepare_receipt(
                    artifact,
                    receipt_id="APPROVAL-VIDEO-01-FUTURE",
                    project_id="SERIE-TEST",
                    video_id="VIDEO-01",
                    created_at="2999-01-01T00:00:00Z",
                )

    def test_approval_requires_verifiable_human_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            artifact = Path(directory) / "video.mov"
            artifact.write_bytes(b"master")
            pending = RECEIPTS.prepare_receipt(
                artifact,
                receipt_id="APPROVAL-VIDEO-01-HUMAN",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            candidate = copy.deepcopy(pending)
            candidate["decision"] = approval_decision()
            candidate["decision"]["approver"] = "codex"
            candidate["decision"]["evidence"]["reference"] = "unverifiable"
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "verifiable human reference"):
                RECEIPTS.seal_receipt(candidate, artifact_override=artifact)

    def test_atomic_write_ignores_predictable_temp_symlink_and_rejects_destination_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            victim = root / "victim.txt"
            victim.write_text("KEEP", encoding="utf-8")
            destination = root / "receipt.json"
            destination.with_name(destination.name + ".tmp").symlink_to(victim)
            with redirect_stdout(StringIO()):
                RECEIPTS.emit_json({"safe": True}, out=destination, write=True)
            self.assertEqual(victim.read_text(encoding="utf-8"), "KEEP")
            destination.unlink()
            destination.symlink_to(victim)
            with self.assertRaisesRegex(RECEIPTS.ApprovalReceiptError, "symlink"):
                RECEIPTS.emit_json({"safe": True}, out=destination, write=True)


class MasterProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hdr_path = FRAMEWORK / "master-profiles/editorial-mezzanine-hdr-001.json"
        cls.sdr_path = FRAMEWORK / "master-profiles/social-delivery-sdr-001.json"
        cls.hdr = MASTERS.load_profile(cls.hdr_path)
        cls.sdr = MASTERS.load_profile(cls.sdr_path)

    def test_profiles_match_schema_and_separate_roles(self):
        schema = json.loads((FRAMEWORK / "schemas/master-profile.schema.json").read_text(encoding="utf-8"))
        for profile in (self.hdr, self.sdr):
            with self.subTest(profile=profile["id"]):
                self.assertEqual(SCHEMAS.validate_document(profile, schema), [])
        self.assertEqual(self.hdr["color_intent"], "preserve_hdr")
        self.assertEqual(self.sdr["color_intent"], "normalize_sdr_bt709")
        self.assertFalse(self.hdr["governance"]["upload_ready"])
        self.assertTrue(self.sdr["governance"]["requires_approved_source_receipt"])

    def test_hdr_mezzanine_fixture_is_compliant_but_not_publication_ready(self):
        metadata = MASTERS.parse_ffprobe(probe_hdr())
        result = MASTERS.evaluate_profile(
            self.hdr,
            metadata,
            media_path="master.mov",
            media_sha256="a" * 64,
        )
        self.assertEqual(result["profile_status"], "compliant")
        self.assertEqual(result["lineage_status"], "not_required")
        self.assertTrue(result["visual_review_required"])
        self.assertFalse(result["publication_ready"])

    def test_hdr_passthrough_fails_sdr_delivery_contract(self):
        metadata = MASTERS.parse_ffprobe(probe_hdr())
        result = MASTERS.evaluate_profile(
            self.sdr,
            metadata,
            media_path="delivery.mp4",
            media_sha256="a" * 64,
            loudness={"integrated_lufs": -14.0, "true_peak_dbtp": -1.2},
        )
        codes = {item["code"] for item in result["findings"]}
        self.assertTrue({"VIDEO_CODEC", "PIXEL_FORMAT", "COLOR_TRANSFER"}.issubset(codes))
        self.assertEqual(result["technical_status"], "failed")

    def test_social_delivery_needs_loudness_and_approved_source(self):
        metadata = MASTERS.parse_ffprobe(probe_sdr())
        result = MASTERS.evaluate_profile(
            self.sdr,
            metadata,
            media_path="delivery.mp4",
            media_sha256="b" * 64,
        )
        self.assertEqual(result["technical_status"], "passed")
        self.assertEqual(result["loudness_status"], "pending")
        self.assertEqual(result["lineage_status"], "pending")
        self.assertEqual(result["profile_status"], "needs_evidence")

    def test_social_delivery_passes_with_exact_approved_source_and_loudness(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "editorial.mov"
            delivery = root / "delivery.mp4"
            source.write_bytes(b"approved-hdr")
            delivery.write_bytes(b"derived-sdr")
            pending = RECEIPTS.prepare_receipt(
                source,
                receipt_id="APPROVAL-VIDEO-01-V2",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                media_role="editorial_mezzanine",
                profile_id=self.hdr["id"],
                created_at=CREATED_AT,
            )
            receipt = approve(pending, source)
            source_hash = RECEIPTS.sha256_file(source)
            delivery_hash = RECEIPTS.sha256_file(delivery)
            result = MASTERS.evaluate_profile(
                self.sdr,
                MASTERS.parse_ffprobe(probe_sdr()),
                media_path=delivery,
                media_sha256=delivery_hash,
                loudness={"integrated_lufs": -14.2, "true_peak_dbtp": -1.1},
                approval_receipt=receipt,
                source_master=source,
                source_profile=self.hdr,
                source_metadata=MASTERS.parse_ffprobe(probe_hdr()),
                expected_project_id="SERIE-TEST",
                expected_video_id="VIDEO-01",
                tone_map_evidence=tone_map_evidence(
                    "SERIE-TEST",
                    "VIDEO-01",
                    source_hash,
                    delivery_hash,
                    self.hdr["id"],
                    self.sdr["id"],
                ),
                visual_review=visual_review("SERIE-TEST", "VIDEO-01", delivery_hash, self.sdr["id"]),
            )
            self.assertEqual(result["technical_status"], "passed")
            self.assertEqual(result["loudness_status"], "passed")
            self.assertEqual(result["lineage_status"], "passed")
            self.assertEqual(result["profile_status"], "compliant")
            self.assertEqual(result["tone_map_status"], "passed")
            self.assertEqual(result["visual_review_status"], "passed")
            self.assertTrue(result["publication_ready"])

    def test_pending_receipt_cannot_unlock_social_master(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "editorial.mov"
            delivery = root / "delivery.mp4"
            source.write_bytes(b"pending-hdr")
            delivery.write_bytes(b"derived-sdr")
            receipt = RECEIPTS.prepare_receipt(
                source,
                receipt_id="APPROVAL-VIDEO-01-V2",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            result = MASTERS.evaluate_profile(
                self.sdr,
                MASTERS.parse_ffprobe(probe_sdr()),
                media_path=delivery,
                media_sha256=RECEIPTS.sha256_file(delivery),
                loudness={"integrated_lufs": -14.0, "true_peak_dbtp": -1.1},
                approval_receipt=receipt,
                source_master=source,
            )
            self.assertEqual(result["lineage_status"], "failed")
            self.assertEqual(result["profile_status"], "failed")

    def test_same_hash_cannot_pose_as_derived_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "editorial.mov"
            delivery = root / "delivery.mp4"
            source.write_bytes(b"same-bytes")
            delivery.write_bytes(b"same-bytes")
            pending = RECEIPTS.prepare_receipt(
                source,
                receipt_id="APPROVAL-VIDEO-01-V2",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                created_at=CREATED_AT,
            )
            receipt = approve(pending, source)
            result = MASTERS.evaluate_profile(
                self.sdr,
                MASTERS.parse_ffprobe(probe_sdr()),
                media_path=delivery,
                media_sha256=RECEIPTS.sha256_file(delivery),
                loudness={"integrated_lufs": -14.0, "true_peak_dbtp": -1.1},
                approval_receipt=receipt,
                source_master=source,
            )
            self.assertEqual(result["lineage_status"], "failed")
            self.assertTrue(
                any("distinct derived artifact" in item["message"] for item in result["findings"])
            )

    def test_loudness_or_true_peak_outside_contract_fails(self):
        metadata = MASTERS.parse_ffprobe(probe_sdr())
        result = MASTERS.evaluate_profile(
            self.sdr,
            metadata,
            media_path="delivery.mp4",
            media_sha256="b" * 64,
            loudness={"integrated_lufs": -20.0, "true_peak_dbtp": 0.0},
        )
        codes = {item["code"] for item in result["findings"]}
        self.assertTrue({"LOUDNESS_OUT_OF_RANGE", "TRUE_PEAK_TOO_HIGH"}.issubset(codes))
        self.assertEqual(result["loudness_status"], "failed")

    def test_loudness_rejects_nan_and_infinity(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(MASTERS.MasterProfileError, "finite"):
                    MASTERS.parse_loudness(
                        {"integrated_lufs": value, "true_peak_dbtp": -1.1}
                    )

        invalid_probe = probe_sdr()
        invalid_probe["streams"][0]["duration"] = "NaN"
        with self.assertRaisesRegex(MASTERS.DeliveryCheckError, "finite"):
            MASTERS.parse_ffprobe(invalid_probe)

    def test_external_probe_and_loudness_must_match_media_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "delivery.mp4"
            media.write_bytes(b"delivery")
            actual_hash = RECEIPTS.sha256_file(media)
            probe_path = root / "probe.json"
            loudness_path = root / "loudness.json"
            probe_path.write_text(
                json.dumps(probe_evidence(probe_sdr(), "a" * 64)), encoding="utf-8"
            )
            loudness_path.write_text(
                json.dumps(loudness_evidence("a" * 64)), encoding="utf-8"
            )
            with self.assertRaisesRegex(MASTERS.MasterProfileError, "does not match"):
                MASTERS.load_probe_evidence(probe_path, actual_hash)
            with self.assertRaisesRegex(MASTERS.MasterProfileError, "does not match"):
                MASTERS.load_loudness_evidence(loudness_path, actual_hash)

    def test_fixture_evidence_is_explicitly_non_authoritative(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "master.mov"
            media.write_bytes(b"master")
            path = root / "probe.json"
            path.write_text(
                json.dumps(probe_evidence(probe_hdr(), None, authoritative=False)),
                encoding="utf-8",
            )
            raw_probe, authoritative, evidence = MASTERS.load_probe_evidence(
                path, RECEIPTS.sha256_file(media)
            )
            result = MASTERS.evaluate_profile(
                self.hdr,
                MASTERS.parse_ffprobe(raw_probe),
                media_path=media,
                media_sha256=RECEIPTS.sha256_file(media),
                probe_authoritative=authoritative,
                probe_evidence=evidence,
            )
            self.assertEqual(result["technical_status"], "needs_evidence")
            self.assertEqual(result["profile_status"], "needs_evidence")

    def test_lineage_rejects_partial_wrong_context_or_non_hdr_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "editorial.mov"
            delivery = root / "delivery.mp4"
            source.write_bytes(b"source")
            delivery.write_bytes(b"delivery")
            pending = RECEIPTS.prepare_receipt(
                source,
                receipt_id="APPROVAL-VIDEO-99-SCOPED",
                project_id="WRONG-PROJECT",
                video_id="VIDEO-99",
                media_role="editorial_mezzanine",
                profile_id=None,
                created_at=CREATED_AT,
            )
            scoped = copy.deepcopy(pending)
            scoped["decision"] = approval_decision(
                whole_artifact=False,
                approved_layers=["captions"],
            )
            scoped = RECEIPTS.seal_receipt(scoped, artifact_override=source)
            result = MASTERS.evaluate_profile(
                self.sdr,
                MASTERS.parse_ffprobe(probe_sdr()),
                media_path=delivery,
                media_sha256=RECEIPTS.sha256_file(delivery),
                loudness={"integrated_lufs": -14.0, "true_peak_dbtp": -1.1},
                approval_receipt=scoped,
                source_master=source,
                source_profile=self.hdr,
                source_metadata=MASTERS.parse_ffprobe(probe_sdr()),
                expected_project_id="SERIE-TEST",
                expected_video_id="VIDEO-01",
            )
            messages = " ".join(item["message"] for item in result["findings"])
            self.assertEqual(result["lineage_status"], "failed")
            self.assertIn("project_id", messages)
            self.assertIn("video_id", messages)
            self.assertIn("source profile", messages)
            self.assertIn("whole-artifact", messages)
            self.assertIn("trusted HDR profile", messages)

    def test_delivery_requires_tone_map_and_bound_human_visual_review(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "editorial.mov"
            delivery = root / "delivery.mp4"
            source.write_bytes(b"source")
            delivery.write_bytes(b"delivery")
            pending = RECEIPTS.prepare_receipt(
                source,
                receipt_id="APPROVAL-VIDEO-01-EVIDENCE",
                project_id="SERIE-TEST",
                video_id="VIDEO-01",
                media_role="editorial_mezzanine",
                profile_id=self.hdr["id"],
                created_at=CREATED_AT,
            )
            receipt = approve(pending, source)
            delivery_hash = RECEIPTS.sha256_file(delivery)
            base = dict(
                media_path=delivery,
                media_sha256=delivery_hash,
                loudness={"integrated_lufs": -14.0, "true_peak_dbtp": -1.1},
                approval_receipt=receipt,
                source_master=source,
                source_profile=self.hdr,
                source_metadata=MASTERS.parse_ffprobe(probe_hdr()),
                expected_project_id="SERIE-TEST",
                expected_video_id="VIDEO-01",
            )
            missing = MASTERS.evaluate_profile(
                self.sdr, MASTERS.parse_ffprobe(probe_sdr()), **base
            )
            self.assertEqual(missing["profile_status"], "needs_evidence")
            self.assertEqual(missing["tone_map_status"], "pending")
            self.assertEqual(missing["visual_review_status"], "pending")

            tone = tone_map_evidence(
                "SERIE-TEST",
                "VIDEO-01",
                RECEIPTS.sha256_file(source),
                delivery_hash,
                self.hdr["id"],
                self.sdr["id"],
            )
            review = visual_review("SERIE-TEST", "VIDEO-01", delivery_hash, self.sdr["id"])
            review["checks"]["skin_tones_natural"] = False
            invalid = MASTERS.evaluate_profile(
                self.sdr,
                MASTERS.parse_ffprobe(probe_sdr()),
                tone_map_evidence=tone,
                visual_review=review,
                **base,
            )
            self.assertEqual(invalid["visual_review_status"], "failed")
            self.assertEqual(invalid["profile_status"], "failed")

    def test_profile_must_use_trusted_path_hash_version_and_active_state(self):
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "profile.json"
            copied.write_text(self.sdr_path.read_text(encoding="utf-8"), encoding="utf-8")
            with self.assertRaisesRegex(MASTERS.MasterProfileError, "loaded from"):
                MASTERS.load_profile(copied)

            altered = copy.deepcopy(self.sdr)
            altered["status"] = "deprecated"
            with self.assertRaisesRegex(MASTERS.MasterProfileError, "active"):
                MASTERS.evaluate_profile(
                    altered,
                    MASTERS.parse_ffprobe(probe_sdr()),
                    media_path="delivery.mp4",
                    media_sha256="b" * 64,
                )

    def test_checker_cli_refuses_report_write_without_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "master.mov"
            probe_path = root / "probe.json"
            report_path = root / "report.json"
            media.write_bytes(b"master")
            probe_path.write_text(
                json.dumps(probe_evidence(probe_hdr(), RECEIPTS.sha256_file(media))),
                encoding="utf-8",
            )
            args = [
                "--profile",
                str(self.hdr_path),
                "--media",
                str(media),
                "--probe-json",
                str(probe_path),
                "--out",
                str(report_path),
            ]
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                code = MASTERS.main(args)
            self.assertEqual(code, 2)
            self.assertFalse(report_path.exists())

    def test_checker_cli_rejects_legacy_unbound_probe_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            media = root / "master.mov"
            probe_path = root / "probe.json"
            media.write_bytes(b"master")
            probe_path.write_text(json.dumps(probe_hdr()), encoding="utf-8")
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                code = MASTERS.main(
                    [
                        "--profile",
                        str(self.hdr_path),
                        "--media",
                        str(media),
                        "--probe-json",
                        str(probe_path),
                    ]
                )
            self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
