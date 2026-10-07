#!/usr/bin/env python3

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
FRAMEWORK = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import golden_master as MODULE  # noqa: E402
import schema_validation as VALIDATOR  # noqa: E402


STAMP = "2026-09-25T12:00:00Z"


class GoldenMasterTests(unittest.TestCase):
    def test_register_compare_and_hash_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_path = root / "golden-master.json"
            artifact = root / "reference.json"
            artifact.write_text('{"schema_version":"1.0.0","value":1}\n', encoding="utf-8")
            registry = MODULE.new_registry("GOLDEN-MASTER-TEST")
            entry = MODULE.register_artifact(
                registry,
                registry_path,
                artifact,
                entry_id="GM-REFERENCE-JSON",
                label="Reference JSON",
                kind="json",
                registered_at=STAMP,
            )
            self.assertEqual(entry["reference_path"], "reference.json")
            MODULE.write_registry(registry_path, registry)

            report = MODULE.compare_registry(MODULE.load_registry(registry_path), registry_path)
            self.assertEqual(report["status"], "match")
            self.assertEqual(report["counts"], {"total": 1, "match": 1, "mismatch": 0})

            artifact.write_text('{"schema_version":"1.0.1","value":2}\n', encoding="utf-8")
            drift = MODULE.compare_registry(MODULE.load_registry(registry_path), registry_path)
            self.assertEqual(drift["status"], "mismatch")
            self.assertNotEqual(drift["comparisons"][0]["status"], "match")

    def test_duplicate_requires_replace_and_registry_stays_sorted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_path = root / "registry.json"
            first = root / "a.txt"
            second = root / "b.txt"
            first.write_text("a", encoding="utf-8")
            second.write_text("b", encoding="utf-8")
            registry = MODULE.new_registry("GOLDEN-MASTER-SORT")
            MODULE.register_artifact(registry, registry_path, second, entry_id="GM-B", label="B", registered_at=STAMP)
            MODULE.register_artifact(registry, registry_path, first, entry_id="GM-A", label="A", registered_at=STAMP)
            self.assertEqual([item["id"] for item in registry["entries"]], ["GM-A", "GM-B"])
            with self.assertRaises(ValueError):
                MODULE.register_artifact(registry, registry_path, first, entry_id="GM-A", label="A2", registered_at=STAMP)
            MODULE.register_artifact(
                registry,
                registry_path,
                first,
                entry_id="GM-A",
                label="A2",
                registered_at=STAMP,
                replace=True,
            )
            self.assertEqual(registry["entries"][0]["label"], "A2")

    def test_registered_document_conforms_to_registry_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_path = root / "registry.json"
            artifact = root / "reference.md"
            artifact.write_text("# reference\n", encoding="utf-8")
            registry = MODULE.new_registry("GOLDEN-MASTER-SCHEMA")
            MODULE.register_artifact(
                registry,
                registry_path,
                artifact,
                entry_id="GM-DOCUMENT",
                label="Reference document",
                registered_at=STAMP,
            )
            schema = json.loads((FRAMEWORK / "schemas/golden-master-registry.schema.json").read_text(encoding="utf-8"))
            self.assertEqual(VALIDATOR.validate_document(registry, schema), [])


if __name__ == "__main__":
    unittest.main()
