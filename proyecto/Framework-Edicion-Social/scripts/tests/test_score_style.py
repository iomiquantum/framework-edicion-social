#!/usr/bin/env python3

import json
import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]
FRAMEWORK = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import schema_validation as VALIDATOR  # noqa: E402
import score_style as MODULE  # noqa: E402


def blueprint(signals=None):
    default = {
        "topic_and_intent": ["technology"],
        "narrative_rhythm": ["process_explanation"],
        "source_geometry": ["talking_head"],
        "platform_fit": ["full_length_reel"],
        "brand_tone": ["high_contrast_editorial"],
    }
    return {"blueprint_id": "CBP-TEST-V1", "style_selection_signals": signals or default}


def catalog(styles):
    return {
        "selection_weights": {
            "topic_and_intent": 0.3,
            "narrative_rhythm": 0.25,
            "source_geometry": 0.2,
            "platform_fit": 0.15,
            "brand_tone": 0.1,
        },
        "styles": styles,
    }


def style(style_id, best_for, avoid_for=(), status="approved"):
    return {
        "id": style_id,
        "status": status,
        "version": "1.0.0",
        "canonical_path": f"styles/{style_id}",
        "best_for": list(best_for),
        "avoid_for": list(avoid_for),
    }


class StyleScoreTests(unittest.TestCase):
    def test_selection_is_deterministic_and_explained(self):
        styles = catalog(
            [
                style(
                    "STYLE_001_MATCH",
                    ["technology", "process_explanation", "talking_head", "full_length_reel", "high_contrast_editorial"],
                ),
                style("STYLE_002_OTHER", ["wellness"], ["technology"]),
            ]
        )
        first = MODULE.build_decision(blueprint(), styles, threshold=0.6, abstention_margin=0.05)
        second = MODULE.build_decision(blueprint(), styles, threshold=0.6, abstention_margin=0.05)
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "selected")
        self.assertEqual(first["selected_style_id"], "STYLE_001_MATCH")
        self.assertIn("Seleccionado", first["explanation"])
        self.assertEqual(first["ranking"][0]["score"], 1.0)

    def test_equal_leaders_abstain_on_margin(self):
        styles = catalog(
            [
                style("STYLE_001_TIE", ["technology"]),
                style("STYLE_002_TIE", ["technology"]),
            ]
        )
        signals = {dimension: ["technology"] for dimension in MODULE.DIMENSIONS}
        decision = MODULE.build_decision(blueprint(signals), styles, threshold=0.6, abstention_margin=0.1)
        self.assertEqual(decision["status"], "abstained")
        self.assertIn("ambiguous_margin", decision["abstention_reasons"])
        self.assertIsNone(decision["selected_style_id"])

    def test_neutral_scores_abstain_below_threshold(self):
        styles = catalog([style("STYLE_001_NEUTRAL", ["wellness"])])
        decision = MODULE.build_decision(blueprint(), styles, threshold=0.75, abstention_margin=0.05)
        self.assertEqual(decision["status"], "abstained")
        self.assertIn("below_threshold", decision["abstention_reasons"])

    def test_repository_blueprint_selects_color_editorial_and_validates(self):
        blueprint_document = json.loads((FRAMEWORK / "templates/creative-blueprint.json").read_text(encoding="utf-8"))
        catalog_document = json.loads((FRAMEWORK / "styles/catalog.json").read_text(encoding="utf-8"))
        decision = MODULE.build_decision(blueprint_document, catalog_document)
        schema = json.loads((FRAMEWORK / "schemas/style-decision.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(decision["selected_style_id"], "STYLE_002_TECH_EDITORIAL_COLOR")
        self.assertEqual(VALIDATOR.validate_document(decision, schema), [])


if __name__ == "__main__":
    unittest.main()
