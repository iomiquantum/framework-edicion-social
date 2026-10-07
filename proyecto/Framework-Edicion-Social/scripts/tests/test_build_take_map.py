#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "build_take_map.py"
SPEC = importlib.util.spec_from_file_location("build_take_map", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def words(tokens):
    result = []
    for index, token in enumerate(tokens):
        result.append({"index": index, "text": token, "token": MODULE.normalize(token), "start": index * 0.2, "end": index * 0.2 + 0.15})
    return result


class MarkerTakeMapTests(unittest.TestCase):
    def test_marker_end_does_not_consume_spoken_content(self):
        source = words(["Marcador", "video", "uno", "toma", "dos", "inicio", "Hola", "este", "es", "el", "contenido", "Marcador", "aprobada", "aprobada"])
        markers = MODULE.detect_markers(source)
        self.assertEqual(markers[0]["kind"], "take_start")
        self.assertEqual(markers[0]["raw"], "Marcador video uno toma dos inicio")
        self.assertAlmostEqual(markers[0]["end_s"], source[5]["end"])
        takes = MODULE.compile_takes(markers, source[-1]["end"])
        self.assertEqual(takes[0]["decision"]["status"], "approved")
        self.assertAlmostEqual(takes[0]["candidate_range"]["start_s"], source[5]["end"])
        self.assertAlmostEqual(takes[0]["candidate_range"]["end_s"], source[11]["start"])

    def test_unclosed_take_is_ambiguous(self):
        source = words(["Marcador", "video", "3", "toma", "1", "inicio", "Contenido", "sin", "cierre"])
        takes = MODULE.compile_takes(MODULE.detect_markers(source), source[-1]["end"])
        self.assertEqual(takes[0]["decision"]["status"], "ambiguous_unclosed")

    def test_discarded_marker(self):
        source = words(["Marcador", "video", "4", "toma", "2", "inicio", "Texto", "Marcador", "descartar", "descartar"])
        takes = MODULE.compile_takes(MODULE.detect_markers(source), source[-1]["end"])
        self.assertEqual(takes[0]["decision"]["status"], "discarded")

    def test_orphan_decision_is_reported(self):
        source = words(["Marcador", "aprobada", "aprobada", "Marcador", "video", "2", "toma", "1", "inicio", "Contenido"])
        takes, orphan_decisions = MODULE.compile_takes_with_diagnostics(MODULE.detect_markers(source), source[-1]["end"])
        self.assertEqual(len(orphan_decisions), 1)
        self.assertEqual(orphan_decisions[0]["kind"], "approved")
        self.assertEqual(takes[0]["decision"]["status"], "ambiguous_unclosed")

    def test_marker_words_must_be_in_protocol_order(self):
        source = words(["Marcador", "inicio", "toma", "1", "video", "2"])
        markers = MODULE.detect_markers(source)
        self.assertEqual(markers[0]["kind"], "unknown")

    def test_take_start_without_inicio_is_detected_with_warning(self):
        source = words(["Marcador", "video", "8", "toma", "6", "Contenido", "Marcador", "aprobado", "aprobado"])
        markers = MODULE.detect_markers(source)
        self.assertEqual(markers[0]["kind"], "take_start")
        self.assertEqual(markers[0]["protocol_variant"], "missing_inicio_keyword")
        self.assertEqual(markers[0]["raw"], "Marcador video 8 toma 6")
        takes = MODULE.compile_takes(markers, source[-1]["end"])
        self.assertEqual(takes[0]["decision"]["status"], "approved")
        self.assertIn("start_marker_missing_inicio_keyword", takes[0]["warnings"])

    def test_duplicate_take_id_is_flagged(self):
        source = words([
            "Marcador", "video", "2", "toma", "1", "inicio", "A",
            "Marcador", "descartar", "descartar",
            "Marcador", "video", "2", "toma", "1", "inicio", "B",
            "Marcador", "aprobada", "aprobada",
        ])
        takes, _ = MODULE.compile_takes_with_diagnostics(MODULE.detect_markers(source), source[-1]["end"])
        self.assertIn("duplicate_take_id", takes[1]["warnings"])

    def test_correction_marker_keeps_take_open_and_records_replacement(self):
        source = words([
            "Marcador", "video", "2", "toma", "1", "inicio",
            "La", "frase", "equivocada",
            "Marcador", "corregir", "corregir", "ultima", "frase",
            "La", "frase", "correcta",
            "Marcador", "aprobada", "aprobada",
        ])
        markers = MODULE.detect_markers(source)
        self.assertEqual(markers[1]["kind"], "replace_previous_phrase")
        self.assertEqual(markers[1]["raw"], "Marcador corregir corregir ultima frase")
        takes = MODULE.compile_takes(markers, source[-1]["end"])
        self.assertEqual(takes[0]["decision"]["status"], "approved")
        self.assertEqual(len(takes[0]["corrections"]), 1)
        correction = takes[0]["corrections"][0]
        self.assertEqual(correction["status"], "pending_audio_review")
        self.assertAlmostEqual(correction["target_range"]["end_s"], source[9]["start"])
        self.assertAlmostEqual(correction["replacement_range"]["start_s"], source[13]["end"])

    def test_correction_outside_take_is_reported_as_orphan(self):
        source = words(["Marcador", "corregir", "corregir", "ultima", "frase"])
        markers = MODULE.detect_markers(source)
        takes, _ = MODULE.compile_takes_with_diagnostics(markers, source[-1]["end"])
        self.assertEqual(takes, [])
        self.assertEqual(len(MODULE.find_orphan_corrections(markers, takes)), 1)


if __name__ == "__main__":
    unittest.main()
