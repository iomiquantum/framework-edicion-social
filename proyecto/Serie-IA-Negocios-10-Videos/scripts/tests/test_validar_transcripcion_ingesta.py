"""Reliability controls, including failure patterns observed in lote16–20."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "validar_transcripcion_ingesta.py"
SPEC = importlib.util.spec_from_file_location("validar_transcripcion_ingesta", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def words(text, start=0, step=.5):
    return [{"text": token, "start": start + i * step, "end": start + (i + 1) * step} for i, token in enumerate(text.split())]


class TranscriptReliabilityTests(unittest.TestCase):
    def codes(self, report):
        return {f["code"] for f in report["findings"]}

    def test_marker_variants_and_object_input(self):
        for text in ["Markador vídeo dieciséis toma dos inicio", "marcador video dieciseis toma 2 inicio", "marcador video 16, toma dos inicio"]:
            result = MODULE.analyze({"words": words(text)}, 8, 16, 16)
            self.assertEqual(result["status"], "pass", result)
            self.assertFalse(result["human_review_completed"])
            self.assertFalse(result["ingest_ready"])

    def test_numbered_reference_without_marker_is_not_coverage(self):
        result = MODULE.analyze(words("mira nuestro video dieciséis esta semana"), 8, 16, 16)
        self.assertIn("VIDEO_COVERAGE_MISSING", self.codes(result))
        self.assertIn("VIDEO_REFERENCE_WITHOUT_MARKER", self.codes(result))

    def test_natural_fillers_and_repeated_corrections_do_not_loop_flag(self):
        text = "marcador video 16 toma uno " + " ".join(["marcador corregir corregir última frase y si no entiendo tu problema probablemente probablemente"] * 5)
        result = MODULE.analyze(words(text), 60, 16, 16)
        self.assertNotIn("MASSIVE_NGRAM_REPETITION", self.codes(result))
        many_markers = MODULE.analyze(words("marcador video 16 toma uno " + "marcador corregir corregir última frase " * 50), 180, 16, 16)
        self.assertNotIn("MASSIVE_NGRAM_REPETITION", self.codes(many_markers))

    def test_massive_phrase_spread_is_a_failure(self):
        text = "marcador video 16 toma uno " + "qué prefieres tú un vendedor que explica mucho o uno que pregunta bien " * 50
        result = MODULE.analyze(words(text, step=.2), 150, 16, 16)
        self.assertEqual(result["status"], "fail")
        self.assertIn("MASSIVE_NGRAM_REPETITION", self.codes(result))

    def test_short_local_repetition_does_not_loop_flag(self):
        text = "marcador video 16 toma uno " + "qué prefieres tú un vendedor que pregunta bien " * 25
        result = MODULE.analyze(words(text, step=.03), 10, 16, 16)
        self.assertNotIn("MASSIVE_NGRAM_REPETITION", self.codes(result))

    def test_many_explicit_sentence_corrections_are_not_massive_loop(self):
        text = "marcador video 16 toma uno " + "marcador corregir corregir última frase qué prefieres tú un vendedor que explica mucho o uno que pregunta bien " * 25
        result = MODULE.analyze(words(text), 260, 16, 16)
        self.assertNotIn("MASSIVE_NGRAM_REPETITION", self.codes(result))

    def test_timestamp_regression_and_chunk_overlap_remain_visible(self):
        data = words("marcador video 16 toma uno") + words("si no entiendo tu problema", start=1)
        result = MODULE.analyze(data, 8, 16, 16)
        self.assertIn("TIMESTAMPS_NON_MONOTONIC", self.codes(result))
        self.assertIn("WORD_TIME_OVERLAP", self.codes(result))
        self.assertEqual(result["status"], "fail")

    def test_duration_zero_ratio_and_overrun(self):
        data = words("marcador video 16 toma uno")
        data[0]["end"] = data[0]["start"]
        data[-1]["end"] = 20
        result = MODULE.analyze(data, 8, 16, 16)
        self.assertIn("ZERO_DURATION_RATIO", self.codes(result))
        self.assertIn("SOURCE_DURATION_EXCEEDED", self.codes(result))

    def test_gaps_are_advisory_and_bad_words_are_errors(self):
        result = MODULE.analyze(words("marcador video 16 toma uno"), 50, 16, 16)
        self.assertEqual(result["status"], "warn")
        self.assertIn("TRANSCRIPT_LONG_GAPS", self.codes(result))
        malformed = MODULE.analyze([{"text": "hola", "start": float("nan"), "end": 2}], 8, 16, 16)
        self.assertIn("WORD_INVALID", self.codes(malformed))


if __name__ == "__main__":
    unittest.main()
