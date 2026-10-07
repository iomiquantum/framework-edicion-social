import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "qa_reuse_context.py"
SPEC = importlib.util.spec_from_file_location("qa_reuse_context", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReuseContextTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.spec_path = self.root / "spec.json"
        self.spec = {"scope_id": "VIDEO-26-FLUJO2", "coverage_note": "Inventario completo declarado manualmente para el candidato.",
                     "groups": {name: [f"{name}.dat"] for name in MODULE.GROUPS}}
        for name in MODULE.GROUPS:
            (self.root / f"{name}.dat").write_text(f"original-{name}", encoding="utf-8")
        self.write_spec()

    def write_spec(self):
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")

    def capture(self, name):
        path = self.root / f"{name}.json"
        MODULE.write_new_json(path, MODULE.snapshot(self.spec_path))
        return path

    def compare(self, before, after, current=True):
        return MODULE.compare_snapshots(before, after, self.spec_path if current else None)

    def assert_rejected(self, report, contains=None):
        self.assertEqual(report["status"], "rejected")
        self.assertEqual(report["reuse_candidate_scopes"], [])
        self.assertEqual(report["rerun_scopes"], list(MODULE.DEPENDENCIES))
        self.assertFalse(report["current_context_verified"])
        self.assertTrue(report["errors"])
        if contains:
            self.assertIn(contains, " ".join(report["errors"]))

    def test_unchanged_is_only_candidate_not_qa_or_approval(self):
        before, after = self.capture("before"), self.capture("after")
        report = self.compare(before, after)
        self.assertEqual(report["status"], "comparison_complete")
        self.assertEqual(report["reuse_candidate_scopes"], list(MODULE.DEPENDENCIES))
        self.assertEqual(report["rerun_scopes"], [])
        self.assertEqual(report["qa_result"], "not_evaluated")
        self.assertEqual(report["approval"], "not_evaluated")
        self.assertEqual(report["exact_export_qa"], "required_for_each_new_mp4")

    def test_visual_asset_change_preserves_audio_candidate(self):
        before = self.capture("before")
        (self.root / "visual_assets.dat").write_text("new-context-image", encoding="utf-8")
        report = self.compare(before, self.capture("after"))
        self.assertEqual(report["changed_groups"], ["visual_assets"])
        self.assertEqual(report["rerun_scopes"], ["visual", "captions", "semantics"])
        self.assertEqual(report["reuse_candidate_scopes"], ["audio"])

    def test_visual_style_html_text_change_invalidates_semantics(self):
        before = self.capture("before")
        (self.root / "visual_style.dat").write_text("<h1>La pregunta</h1>", encoding="utf-8")
        report = self.compare(before, self.capture("after"))
        self.assertEqual(report["changed_groups"], ["visual_style"])
        self.assertEqual(report["rerun_scopes"], ["visual", "captions", "semantics"])
        self.assertEqual(report["reuse_candidate_scopes"], ["audio"])

    def test_engine_change_invalidates_every_scope(self):
        before = self.capture("before")
        (self.root / "engine.dat").write_text("renderer-configuration-v2", encoding="utf-8")
        report = self.compare(before, self.capture("after"))
        self.assertEqual(report["changed_groups"], ["engine"])
        self.assertEqual(report["rerun_scopes"], list(MODULE.DEPENDENCIES))
        self.assertEqual(report["reuse_candidate_scopes"], [])

    def test_each_family_has_expected_scope_dependencies(self):
        original = {name: (self.root / f"{name}.dat").read_text() for name in MODULE.GROUPS}
        before = self.capture("before")
        for index, name in enumerate(MODULE.GROUPS):
            with self.subTest(group=name):
                path = self.root / f"{name}.dat"
                path.write_text(original[name] + "-changed")
                report = self.compare(before, self.capture(f"after-{index}"))
                expected = [scope for scope, groups in MODULE.DEPENDENCIES.items() if name in groups]
                self.assertEqual(report["rerun_scopes"], expected)
                self.assertEqual(report["status"], "comparison_complete")
                path.write_text(original[name])

    def test_current_file_missing_or_changed_rejects_stale_snapshot(self):
        before, after = self.capture("before"), self.capture("after")
        path = self.root / "mix.dat"
        path.write_text("changed-after-snapshot")
        self.assert_rejected(self.compare(before, after), "stale after snapshot")
        path.unlink()
        self.assert_rejected(self.compare(before, after), "missing or unreadable")

    def test_historical_sources_not_rehashed_when_replaced(self):
        before = self.capture("before")
        (self.root / "replacement-source.dat").write_text("new-take")
        self.spec["groups"]["source"] = ["replacement-source.dat"]
        self.write_spec()
        after = self.capture("after")
        (self.root / "source.dat").unlink()
        report = self.compare(before, after)
        self.assertEqual(report["status"], "comparison_complete")
        self.assertIn("source", report["changed_groups"])
        self.assertEqual(report["rerun_scopes"], ["visual", "audio", "semantics"])

    def test_current_spec_is_required_and_byte_bound(self):
        before, after = self.capture("before"), self.capture("after")
        self.assert_rejected(self.compare(before, after, False), "--current-spec is required")
        self.spec_path.write_text(self.spec_path.read_text() + "\n")
        self.assert_rejected(self.compare(before, after), "current spec bytes and descriptor")

    def test_unknown_or_missing_groups_and_empty_required_groups_rejected(self):
        for mutation in ("unknown", "missing", "empty-source", "empty-engine"):
            with self.subTest(mutation=mutation):
                original = copy.deepcopy(self.spec)
                if mutation == "unknown":
                    self.spec["groups"]["untracked"] = []
                elif mutation == "missing":
                    del self.spec["groups"]["mix"]
                else:
                    self.spec["groups"][mutation.removeprefix("empty-")] = []
                self.write_spec()
                with self.assertRaises(MODULE.ContextError):
                    MODULE.snapshot(self.spec_path)
                self.spec = original
        self.write_spec()

    def test_optional_empty_groups_allowed_but_unlisted_dependencies_not_certified(self):
        for name in MODULE.GROUPS:
            if name not in {"source", "engine"}:
                self.spec["groups"][name] = []
        self.write_spec()
        snapshot = MODULE.snapshot(self.spec_path)
        self.assertEqual(snapshot["groups"]["audio_assets"]["files"], [])
        self.assertEqual(snapshot["inventory_scope"], "manually_declared_only")
        self.assertIn("unlisted dependencies are not discovered", snapshot["limits"])

    def test_context_change_rejects_all_reuse(self):
        before = self.capture("before")
        self.spec["scope_id"] = "VIDEO-27-FLUJO2"
        self.write_spec()
        self.assert_rejected(self.compare(before, self.capture("after")), "contexts differ")

    def test_tampered_snapshot_and_resealed_unknown_inventory_rejected(self):
        before, after = self.capture("before"), self.capture("after")
        value = json.loads(after.read_text())
        value["scope_id"] = "FORGED"
        after.write_text(json.dumps(value))
        self.assert_rejected(self.compare(before, after), "integrity_digest mismatch")
        value = MODULE.snapshot(self.spec_path)
        value["groups"]["unknown"] = {"files": [], "sha256": MODULE.digest([])}
        value = MODULE.seal({key: item for key, item in value.items() if key != "integrity_digest"})
        after.write_text(json.dumps(value))
        self.assert_rejected(self.compare(before, after), "snapshot.groups fields")

    def test_paths_relative_to_spec_and_order_independent_group_hash(self):
        extra = self.root / "extra.svg"
        extra.write_text("extra")
        self.spec["groups"]["visual_assets"].append("extra.svg")
        self.write_spec()
        first = MODULE.snapshot(self.spec_path)
        self.spec["groups"]["visual_assets"].reverse()
        self.write_spec()
        second = MODULE.snapshot(self.spec_path)
        self.assertEqual(first["groups"]["visual_assets"], second["groups"]["visual_assets"])
        for file in first["groups"]["visual_assets"]["files"]:
            self.assertTrue(Path(file["path"]).is_absolute())

    def test_directory_duplicate_path_and_missing_file_rejected(self):
        for paths in (["."], ["source.dat", "./source.dat"], ["missing.dat"]):
            with self.subTest(paths=paths):
                self.spec["groups"]["source"] = paths
                self.write_spec()
                with self.assertRaises(MODULE.ContextError):
                    MODULE.snapshot(self.spec_path)

    def test_cli_fail_closed_report_and_no_overwrite(self):
        before, after = self.capture("before"), self.capture("after")
        out = self.root / "comparison.json"
        command = [sys.executable, str(SCRIPT), "compare", "--before", str(before),
                   "--after", str(after), "--out", str(out)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assert_rejected(json.loads(out.read_text()), "--current-spec is required")
        frozen = out.read_bytes()
        result = subprocess.run(command + ["--current-spec", str(self.spec_path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(out.read_bytes(), frozen)
        self.assertIn("File exists", result.stderr)
        valid_out = self.root / "valid-comparison.json"
        command[command.index(str(out))] = str(valid_out)
        result = subprocess.run(command + ["--current-spec", str(self.spec_path)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(valid_out.read_text())["status"], "comparison_complete")


if __name__ == "__main__":
    unittest.main()
