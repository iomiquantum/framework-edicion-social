#!/usr/bin/env python3

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
FRAMEWORK = SCRIPTS.parent
SCRIPT = SCRIPTS / "build_review_packet.py"
SPEC = importlib.util.spec_from_file_location("build_review_packet", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class ReviewPacketTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name).resolve()
        self.render = self.root / "renders/current.mp4"
        self.render.parent.mkdir(parents=True)
        self.render.write_bytes(b"review-render-v2")
        digest = hashlib.sha256(self.render.read_bytes()).hexdigest()
        self.manifest = self.root / "renders/current.manifest.json"
        write_json(
            self.manifest,
            {
                "schema_version": "1.0.0",
                "project_id": "project-review",
                "video_id": "VIDEO-02",
                "output": {
                    "path": "current.mp4",
                    "sha256": digest,
                    "size_bytes": self.render.stat().st_size,
                    "duration_s": 6,
                    "resolution": "1080x1920",
                    "fps": 30,
                    "video_codec": "h264",
                    "audio_codec": "aac",
                    "color": "bt709",
                },
                "review": {
                    "layer_states": {"lookdev": "reused"},
                    "findings": {"technical": [], "semantic": [], "variety": []},
                },
                "qa": {"lint_errors": 0, "runtime_errors": 0},
            },
        )
        self.blueprint = self.root / "creative-blueprint.json"
        write_json(
            self.blueprint,
            {
                "project_id": "project-review",
                "video_id": "VIDEO-02",
                "beats": [
                    {
                        "id": "BEAT-01",
                        "narrative_role": "hook",
                        "narrative_job": "Abrir el problema",
                        "start_s": 0,
                        "end_s": 2,
                    },
                    {
                        "id": "BEAT-02",
                        "narrative_role": "contrast",
                        "narrative_job": "Cambiar de perspectiva",
                        "start_s": 2,
                        "end_s": 4,
                    },
                    {
                        "id": "BEAT-03",
                        "narrative_role": "cta",
                        "narrative_job": "Cerrar",
                        "start_s": 4,
                        "end_s": 6,
                    },
                ],
            },
        )
        mapping = json.loads((FRAMEWORK / "templates/dependency-map.json").read_text(encoding="utf-8"))
        mapping["project_id"] = "project-review"
        self.dependency_map = self.root / "dependency-map.json"
        write_json(self.dependency_map, mapping)
        self.changes = self.root / "changes.json"
        write_json(
            self.changes,
            {
                "changes": [
                    {
                        "id": "CHANGE-001",
                        "start_s": 2.4,
                        "end_s": 3.1,
                        "layer": "lookdev",
                        "element_id": "diagram-primary",
                        "instruction": "Reducir la escala y mover al espacio negativo.",
                    }
                ]
            },
        )

    def tearDown(self):
        self.temporary.cleanup()

    def build(self, **overrides):
        values = {
            "root": self.root,
            "render_path": self.render,
            "manifest_path": self.manifest,
            "dependency_map_path": self.dependency_map,
            "project_id": "project-review",
            "video_id": "VIDEO-02",
            "blueprint_path": self.blueprint,
            "changes_path": self.changes,
            "generated_at": "2026-09-25T12:00:00Z",
        }
        values.update(overrides)
        return MODULE.build_packet(**values)

    def cli_args(self):
        return [
            "--project-root", str(self.root),
            "--project-id", "project-review",
            "--video-id", "VIDEO-02",
            "--render", str(self.render),
            "--manifest", str(self.manifest),
            "--dependency-map", str(self.dependency_map),
            "--blueprint", str(self.blueprint),
            "--changes", str(self.changes),
        ]

    def write_review_decision(self, path, *, status="changes_requested"):
        write_json(
            path,
            {
                "schema_version": "1.0.0",
                "project_id": "project-review",
                "review_id": "REVIEW-002",
                "reviewed_at": "2026-09-25T12:00:00Z",
                "review_artifact": "current.mp4",
                "source_manifest_sha256": hashlib.sha256(self.manifest.read_bytes()).hexdigest(),
                "overall_decision": status,
                "approved_layers": [],
                "changes": [],
                "preference_candidates": [],
                "requires_full_editorial_recheck": status == "changes_requested",
                "requires_new_full_render": status == "changes_requested",
                "notes": "Decisión editorial de prueba; no es un recibo de aprobación.",
            },
        )

    def test_builds_hash_bound_packet_with_impact_and_partial_preview(self):
        packet = self.build()
        self.assertEqual(packet["render"]["sha256"], hashlib.sha256(self.render.read_bytes()).hexdigest())
        self.assertEqual(packet["source_manifest"]["path"], "renders/current.manifest.json")
        self.assertEqual(
            packet["inputs"]["dependency_map"]["sha256"],
            hashlib.sha256(self.dependency_map.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            packet["inputs"]["blueprint"]["sha256"],
            hashlib.sha256(self.blueprint.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            packet["inputs"]["changes"]["sha256"],
            hashlib.sha256(self.changes.read_bytes()).hexdigest(),
        )
        self.assertIsNone(packet["inputs"]["review_decision"])
        self.assertFalse(packet["governance"]["review_decision_replaces_approval_receipt"])
        self.assertEqual(packet["governance"]["approval_authority"], "approval_receipt_only")
        self.assertEqual(packet["beats"][0]["review_tags"], ["hook"])
        self.assertIn("middle", packet["beats"][1]["review_tags"])
        self.assertIn("critical_transition", packet["beats"][1]["review_tags"])
        self.assertEqual(packet["preview_plan"]["strategy"], "partial_then_full")
        self.assertTrue(packet["preview_plan"]["final_delivery_requires_full_encode"])
        self.assertEqual(packet["preview_plan"]["ranges"][0]["change_ids"], ["CHANGE-001"])
        self.assertEqual(
            [item["id"] for item in packet["impact"]["invalidated_layers"]],
            ["lookdev", "assembly", "qa", "render"],
        )
        states = {item["id"]: item["state"] for item in packet["layers"]}
        self.assertEqual(states["lookdev"], "modified")
        self.assertEqual(states["assembly"], "invalidated")
        self.assertEqual(MODULE.schema_errors(packet), [])

    def test_manifest_hash_size_and_path_are_verified(self):
        document = json.loads(self.manifest.read_text(encoding="utf-8"))
        document["output"]["sha256"] = "f" * 64
        write_json(self.manifest, document)
        with self.assertRaisesRegex(MODULE.ReviewPacketError, "SHA-256"):
            self.build()

    def test_change_range_and_layer_fail_closed(self):
        document = json.loads(self.changes.read_text(encoding="utf-8"))
        document["changes"][0]["end_s"] = 9
        write_json(self.changes, document)
        with self.assertRaisesRegex(MODULE.ReviewPacketError, "beyond"):
            self.build()

        document["changes"][0]["end_s"] = 3
        document["changes"][0]["layer"] = "captions"
        write_json(self.changes, document)
        with self.assertRaisesRegex(MODULE.ReviewPacketError, "dependency-map layer"):
            self.build()

    def test_beats_are_required_and_cannot_overlap(self):
        with self.assertRaisesRegex(MODULE.ReviewPacketError, "traceable beat"):
            self.build(blueprint_path=None)
        blueprint = json.loads(self.blueprint.read_text(encoding="utf-8"))
        blueprint["beats"][1]["start_s"] = 1.5
        write_json(self.blueprint, blueprint)
        with self.assertRaisesRegex(MODULE.ReviewPacketError, "overlap"):
            self.build()

    def test_optional_previous_render_is_bound_for_comparison(self):
        previous = self.root / "renders/previous.mp4"
        previous.write_bytes(b"review-render-v1")
        packet = self.build(previous_render_path=previous)
        self.assertTrue(packet["comparison"]["enabled"])
        self.assertEqual(packet["comparison"]["relation"], "different")
        self.assertEqual(packet["comparison"]["previous"]["path"], "renders/previous.mp4")

    def test_review_decision_must_bind_same_manifest_and_does_not_approve_other_scopes(self):
        decision = self.root / "review-decision.json"
        self.write_review_decision(decision)
        packet = self.build(review_decision_path=decision)
        self.assertEqual(packet["decisions"]["video"]["status"], "changes_requested")
        self.assertEqual(packet["decisions"]["assets"]["status"], "pending")
        self.assertEqual(packet["decisions"]["template_family"]["status"], "pending")
        self.assertEqual(
            packet["inputs"]["review_decision"]["sha256"],
            hashlib.sha256(decision.read_bytes()).hexdigest(),
        )

        document = json.loads(decision.read_text(encoding="utf-8"))
        document["source_manifest_sha256"] = "0" * 64
        write_json(decision, document)
        with self.assertRaisesRegex(MODULE.ReviewPacketError, "not bound"):
            self.build(review_decision_path=decision)

    def test_review_decision_is_schema_validated_and_never_becomes_receipt(self):
        decision = self.root / "review-decision.json"
        write_json(
            decision,
            {
                "project_id": "project-review",
                "review_id": "REVIEW-002",
                "review_artifact": "current.mp4",
                "source_manifest_sha256": hashlib.sha256(self.manifest.read_bytes()).hexdigest(),
                "overall_decision": "changes_requested",
            },
        )
        with self.assertRaisesRegex(MODULE.ReviewPacketError, "review-decision.schema.json"):
            self.build(review_decision_path=decision)

        self.write_review_decision(decision, status="approved")
        packet = self.build(review_decision_path=decision, changes_path=None)
        self.assertEqual(packet["decisions"]["video"]["status"], "approved")
        self.assertEqual(packet["governance"]["approval_authority"], "approval_receipt_only")
        self.assertIn("no sustituye", packet["governance"]["notice"])

    def test_hash_bound_inputs_detect_drift_before_write(self):
        packet = self.build()
        blueprint = json.loads(self.blueprint.read_text(encoding="utf-8"))
        blueprint["beats"][0]["narrative_job"] = "Texto alterado después del paquete"
        write_json(self.blueprint, blueprint)
        with self.assertRaisesRegex(MODULE.ReviewPacketError, "creative blueprint drifted"):
            MODULE.verify_packet_bindings(packet, self.root)
        output = self.root / "review"
        with self.assertRaisesRegex(MODULE.ReviewPacketError, "creative blueprint drifted"):
            MODULE.write_packet(output, packet, self.root)
        self.assertFalse(output.exists())

    def test_html_escapes_review_text_and_contains_form_and_video(self):
        document = json.loads(self.changes.read_text(encoding="utf-8"))
        document["changes"][0]["instruction"] = "<script>alert(1)</script>"
        write_json(self.changes, document)
        packet = self.build()
        output = self.root / "review"
        output.mkdir()
        result = MODULE.render_html(packet, output, self.root)
        self.assertIn("<video", result)
        self.assertIn('name="start_s"', result)
        self.assertIn('name="element_id"', result)
        self.assertNotIn("<script>alert(1)</script>", result)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", result)
        self.assertIn("no sustituye el recibo de aprobación independiente", result)

    def test_cli_is_read_only_without_write_and_requires_write_out_pair(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(MODULE.main(self.cli_args()), 0)
        self.assertIn('"packet_id"', stdout.getvalue())
        self.assertFalse((self.root / "review/review-packet.json").exists())

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.assertEqual(MODULE.main([*self.cli_args(), "--out", "review"]), 2)
        self.assertIn("must be supplied together", stderr.getvalue())

    def test_cli_writes_both_artifacts_only_with_explicit_flags(self):
        with contextlib.redirect_stdout(io.StringIO()):
            result = MODULE.main([*self.cli_args(), "--out", "review", "--write"])
        self.assertEqual(result, 0)
        packet = self.root / "review/review-packet.json"
        page = self.root / "review/review.html"
        self.assertTrue(packet.is_file())
        self.assertTrue(page.is_file())
        self.assertEqual(MODULE.schema_errors(json.loads(packet.read_text(encoding="utf-8"))), [])

    def test_paths_outside_root_and_symlinks_are_rejected(self):
        outside = self.root.parent / f"outside-{self.root.name}.mp4"
        outside.write_bytes(b"outside")
        try:
            with self.assertRaisesRegex(MODULE.ReviewPacketError, "escapes project root"):
                MODULE.safe_input_path(self.root, outside, "render")
            link = self.root / "linked.mp4"
            try:
                os.symlink(self.render, link)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks are unavailable")
            with self.assertRaisesRegex(MODULE.ReviewPacketError, "cannot be a symlink"):
                MODULE.safe_input_path(self.root, link, "render")
        finally:
            outside.unlink(missing_ok=True)

    def test_template_matches_supported_schema(self):
        template = json.loads((FRAMEWORK / "templates/review-packet.json").read_text(encoding="utf-8"))
        self.assertEqual(MODULE.schema_errors(template), [])


if __name__ == "__main__":
    unittest.main()
