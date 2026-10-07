#!/usr/bin/env python3

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "schema_validation.py"
SPEC = importlib.util.spec_from_file_location("schema_validation", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SimpleSchemaValidationTests(unittest.TestCase):
    def test_nested_object_is_actually_validated(self):
        schema = {
            "type": "object",
            "required": ["name", "items"],
            "properties": {
                "name": {"type": "string", "minLength": 3, "pattern": "abc"},
                "items": {
                    "type": "array",
                    "minItems": 1,
                    "uniqueItems": True,
                    "items": {"type": "integer", "minimum": 1},
                },
            },
            "additionalProperties": False,
        }
        self.assertEqual(MODULE.validate_document({"name": "xabcx", "items": [1, 2]}, schema), [])
        errors = MODULE.validate_document({"name": "ab", "items": [0, 0], "extra": True}, schema)
        self.assertTrue(any("shorter" in error for error in errors))
        self.assertTrue(any("lower" in error for error in errors))
        self.assertTrue(any("not unique" in error for error in errors))
        self.assertTrue(any("unexpected property" in error for error in errors))

    def test_empty_date_and_boolean_integer_are_rejected(self):
        date_errors = MODULE.validate_document("", {"type": "string", "format": "date"})
        integer_errors = MODULE.validate_document(True, {"type": "integer"})
        self.assertTrue(date_errors)
        self.assertTrue(integer_errors)
        self.assertTrue(MODULE.validate_document(1, {"const": True}))
        self.assertTrue(MODULE.validate_document(False, {"enum": [0]}))

    def test_rfc3339_formats_are_strict(self):
        date_schema = {"type": "string", "format": "date"}
        datetime_schema = {"type": "string", "format": "date-time"}
        self.assertEqual(MODULE.validate_document("2026-09-25", date_schema), [])
        self.assertEqual(MODULE.validate_document("2026-09-25T12:34:56Z", datetime_schema), [])
        for value in ("20260925", "2026-W39-5", "2026-9-25"):
            with self.subTest(value=value):
                self.assertTrue(MODULE.validate_document(value, date_schema))
        for value in ("20260925T123456Z", "2026-09-25 12:34:56Z", "2026-09-25T12:34Z"):
            with self.subTest(value=value):
                self.assertTrue(MODULE.validate_document(value, datetime_schema))

    def test_integer_uses_json_schema_mathematical_value_semantics(self):
        schema = {"type": "integer"}
        self.assertEqual(MODULE.validate_document(1, schema), [])
        self.assertEqual(MODULE.validate_document(1.0, schema), [])
        self.assertEqual(MODULE.validate_document(1e3, schema), [])
        self.assertTrue(MODULE.validate_document(1.5, schema))
        self.assertTrue(MODULE.validate_document(True, schema))

    def test_unique_items_treats_equivalent_numbers_as_duplicates(self):
        errors = MODULE.validate_document([1, 1.0], {"type": "array", "uniqueItems": True})
        self.assertTrue(errors)

    def test_advanced_or_unknown_keywords_fail_closed(self):
        for schema in (
            {"allOf": [{"type": "string"}]},
            {"type": "string", "format": "uri"},
            {"type": "array", "items": None},
            {"type": "string", "pattern": "["},
        ):
            with self.subTest(schema=schema):
                with self.assertRaises(MODULE.UnsupportedSchemaKeyword):
                    MODULE.assert_supported_schema(schema)

    def test_additional_property_schema_is_enforced(self):
        schema = {
            "type": "object",
            "additionalProperties": {"type": "string", "minLength": 1},
        }
        self.assertEqual(MODULE.validate_document({"ok": "yes"}, schema), [])
        self.assertTrue(MODULE.validate_document({"bad": ""}, schema))


if __name__ == "__main__":
    unittest.main()
