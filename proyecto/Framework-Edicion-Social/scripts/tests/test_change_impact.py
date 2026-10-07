#!/usr/bin/env python3

import copy
import importlib.util
import json
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "change_impact.py"
SPEC = importlib.util.spec_from_file_location("change_impact", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
TEMPLATE = Path(__file__).resolve().parents[2] / "templates/dependency-map.json"


class ChangeImpactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    def test_style_change_propagates_only_to_downstream_layers(self):
        result = MODULE.calculate_impact(self.mapping, ["style"])
        self.assertEqual(
            [item["id"] for item in result["invalidated_layers"]],
            ["lookdev", "assembly", "qa", "render"],
        )
        self.assertEqual(result["heavy_layers"], ["assembly", "render"])
        self.assertNotIn("mixdown", [item["id"] for item in result["invalidated_artifacts"]])

    def test_source_change_reaches_picture_audio_qa_and_render(self):
        result = MODULE.calculate_impact(self.mapping, ["source"])
        ids = [item["id"] for item in result["invalidated_layers"]]
        self.assertEqual(ids, ["ingest", "assembly", "audio-mix", "qa", "render"])
        self.assertIn("delivery-render", [item["id"] for item in result["invalidated_artifacts"]])

    def test_changed_layer_invalidates_itself_and_consumers(self):
        result = MODULE.calculate_impact(self.mapping, ["assembly"])
        self.assertEqual(
            [item["id"] for item in result["invalidated_layers"]],
            ["assembly", "qa", "render"],
        )

    def test_unknown_dependency_and_cycle_fail_closed(self):
        unknown = copy.deepcopy(self.mapping)
        unknown["layers"][0]["depends_on"] = ["missing"]
        with self.assertRaisesRegex(MODULE.DependencyMapError, "unknown dependency"):
            MODULE.validate_dependency_map(unknown)

        cyclic = copy.deepcopy(self.mapping)
        cyclic["layers"][0]["depends_on"] = ["render"]
        with self.assertRaisesRegex(MODULE.DependencyMapError, "cycle"):
            MODULE.validate_dependency_map(cyclic)

    def test_unknown_changed_id_is_an_error(self):
        with self.assertRaisesRegex(MODULE.DependencyMapError, "unknown changed"):
            MODULE.calculate_impact(self.mapping, ["imaginary-input"])


if __name__ == "__main__":
    unittest.main()
