#!/usr/bin/env python3
"""Dependency-free validation for the framework's deliberately simple schemas.

This module is intentionally not a general JSON Schema implementation. It
validates every keyword in the supported subset and refuses schemas containing
advanced or unknown keywords instead of silently ignoring them. Schemas that
use ``$ref``, combinators, or conditionals must be checked by dedicated semantic
code or a complete Draft 2020-12 validator.

Numeric types follow Draft 2020-12 value semantics: a finite float with no
fractional part (for example ``1.0``) satisfies ``type: integer``. Booleans are
always distinct from numbers despite Python's ``True == 1`` behavior.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import date, datetime
from pathlib import Path


ANNOTATION_KEYWORDS = {
    "$schema",
    "$id",
    "title",
    "description",
    "default",
    "examples",
    "deprecated",
    "readOnly",
    "writeOnly",
}

SUPPORTED_VALIDATION_KEYWORDS = {
    "type",
    "enum",
    "const",
    "required",
    "properties",
    "additionalProperties",
    "items",
    "minItems",
    "maxItems",
    "uniqueItems",
    "minLength",
    "maxLength",
    "pattern",
    "format",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "minProperties",
    "maxProperties",
}
JSON_TYPES = {"null", "object", "array", "string", "integer", "number", "boolean"}
SUPPORTED_FORMATS = {"date", "date-time"}
FULL_DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
DATE_TIME_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?"
    r"(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
NONNEGATIVE_INTEGER_KEYWORDS = {
    "minItems",
    "maxItems",
    "minLength",
    "maxLength",
    "minProperties",
    "maxProperties",
}
NUMERIC_KEYWORDS = {"minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum"}


class UnsupportedSchemaKeyword(ValueError):
    """Raised when a schema exceeds the validator's explicit subset."""


def load_json(path: Path | str):
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _matches_type(value, expected):
    if expected == "null":
        return value is None
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
            or isinstance(value, float)
            and math.isfinite(value)
            and value.is_integer()
        )
    if expected == "number":
        return (
            isinstance(value, int)
            and not isinstance(value, bool)
            or isinstance(value, float)
            and math.isfinite(value)
        )
    if expected == "boolean":
        return isinstance(value, bool)
    return False


def _json_equal(left, right):
    """JSON equality with booleans kept distinct from numbers."""
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, list):
        return len(left) == len(right) and all(_json_equal(a, b) for a, b in zip(left, right))
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(_json_equal(left[key], right[key]) for key in left)
    return left == right


def assert_supported_schema(schema, path="$schema"):
    """Fail closed when a schema uses a keyword this module cannot enforce."""
    if isinstance(schema, bool):
        return
    if not isinstance(schema, dict):
        raise UnsupportedSchemaKeyword(f"{path}: schema must be an object or boolean")

    allowed = ANNOTATION_KEYWORDS | SUPPORTED_VALIDATION_KEYWORDS
    for keyword in schema:
        if keyword not in allowed:
            raise UnsupportedSchemaKeyword(
                f"{path}: unsupported keyword {keyword!r}; use a full validator or dedicated semantic checks"
            )

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if (
            not expected_types
            or not all(isinstance(item, str) and item in JSON_TYPES for item in expected_types)
            or len(expected_types) != len(set(expected_types))
        ):
            raise UnsupportedSchemaKeyword(f"{path}.type: expected unique names from {sorted(JSON_TYPES)}")

    if "enum" in schema:
        enum = schema["enum"]
        if not isinstance(enum, list) or not enum:
            raise UnsupportedSchemaKeyword(f"{path}.enum: expected a non-empty array")
    required = schema.get("required", [])
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        raise UnsupportedSchemaKeyword(f"{path}.required: expected an array of strings")
    if len(required) != len(set(required)):
        raise UnsupportedSchemaKeyword(f"{path}.required: values must be unique")
    for keyword in NONNEGATIVE_INTEGER_KEYWORDS:
        if keyword in schema:
            value = schema[keyword]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise UnsupportedSchemaKeyword(f"{path}.{keyword}: expected a non-negative integer")
    for keyword in NUMERIC_KEYWORDS:
        if keyword in schema:
            value = schema[keyword]
            if not _matches_type(value, "number"):
                raise UnsupportedSchemaKeyword(f"{path}.{keyword}: expected a finite number")
    if "uniqueItems" in schema and not isinstance(schema["uniqueItems"], bool):
        raise UnsupportedSchemaKeyword(f"{path}.uniqueItems: expected boolean")
    if "pattern" in schema:
        pattern = schema["pattern"]
        if not isinstance(pattern, str):
            raise UnsupportedSchemaKeyword(f"{path}.pattern: expected string")
        try:
            re.compile(pattern)
        except re.error as error:
            raise UnsupportedSchemaKeyword(f"{path}.pattern: invalid regular expression: {error}") from error
    if "format" in schema:
        format_name = schema["format"]
        if not isinstance(format_name, str) or format_name not in SUPPORTED_FORMATS:
            raise UnsupportedSchemaKeyword(
                f"{path}.format: unsupported format {format_name!r}; supported: {sorted(SUPPORTED_FORMATS)}"
            )

    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        raise UnsupportedSchemaKeyword(f"{path}.properties: expected object")
    for name, child in properties.items():
        assert_supported_schema(child, f"{path}.properties.{name}")

    if "items" in schema:
        items = schema["items"]
        if isinstance(items, list):
            raise UnsupportedSchemaKeyword(f"{path}.items: tuple schemas are not supported")
        assert_supported_schema(items, f"{path}.items")

    additional = schema.get("additionalProperties")
    if isinstance(additional, dict):
        assert_supported_schema(additional, f"{path}.additionalProperties")
    elif additional is not None and not isinstance(additional, bool):
        raise UnsupportedSchemaKeyword(f"{path}.additionalProperties: expected boolean or schema")


def _format_error(value, format_name):
    if not isinstance(value, str):
        return f"{value!r} is not a string for format {format_name}"
    try:
        if format_name == "date":
            if not FULL_DATE_PATTERN.fullmatch(value):
                return f"{value!r} is not an RFC 3339 full-date"
            date.fromisoformat(value)
        elif format_name == "date-time":
            if not DATE_TIME_PATTERN.fullmatch(value):
                return f"{value!r} is not an RFC 3339 date-time"
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            return f"unsupported format {format_name!r}"
    except (TypeError, ValueError):
        return f"{value!r} is not a valid ISO {format_name}"
    return None


def _validate(value, schema, path):
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: value is forbidden by schema"]

    errors = []
    expected = schema.get("type")
    if expected is not None:
        allowed = expected if isinstance(expected, list) else [expected]
        if not all(isinstance(item, str) for item in allowed):
            return [f"{path}: schema type must be a string or array of strings"]
        if not any(_matches_type(value, item) for item in allowed):
            return [f"{path}: expected type {allowed}, got {type(value).__name__}"]

    if "const" in schema and not _json_equal(value, schema["const"]):
        errors.append(f"{path}: {value!r} does not equal required constant {schema['const']!r}")
    if "enum" in schema and not any(_json_equal(value, option) for option in schema["enum"]):
        errors.append(f"{path}: {value!r} is not one of {schema['enum']!r}")

    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: string is longer than {schema['maxLength']}")
        pattern = schema.get("pattern")
        if pattern:
            try:
                matched = re.search(pattern, value) is not None
            except re.error as error:
                errors.append(f"{path}: invalid schema regex {pattern!r}: {error}")
            else:
                if not matched:
                    errors.append(f"{path}: {value!r} does not match {pattern!r}")
        if schema.get("format"):
            message = _format_error(value, schema["format"])
            if message:
                errors.append(f"{path}: {message}")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if isinstance(value, float) and not math.isfinite(value):
            errors.append(f"{path}: number must be finite")
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} is lower than {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} is greater than {schema['maximum']}")
        if "exclusiveMinimum" in schema and value <= schema["exclusiveMinimum"]:
            errors.append(f"{path}: {value} is not greater than {schema['exclusiveMinimum']}")
        if "exclusiveMaximum" in schema and value >= schema["exclusiveMaximum"]:
            errors.append(f"{path}: {value} is not lower than {schema['exclusiveMaximum']}")

    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            errors.append(f"{path}: array has fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: array has more than {schema['maxItems']} items")
        if schema.get("uniqueItems"):
            duplicate = any(
                _json_equal(value[left], value[right])
                for left in range(len(value))
                for right in range(left + 1, len(value))
            )
            if duplicate:
                errors.append(f"{path}: array items are not unique")
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                errors.extend(_validate(item, item_schema, f"{path}[{index}]"))

    if isinstance(value, dict):
        if len(value) < schema.get("minProperties", 0):
            errors.append(f"{path}: object has fewer than {schema['minProperties']} properties")
        if "maxProperties" in schema and len(value) > schema["maxProperties"]:
            errors.append(f"{path}: object has more than {schema['maxProperties']} properties")
        properties = schema.get("properties", {})
        for required in schema.get("required", []):
            if required not in value:
                errors.append(f"{path}: missing required property {required!r}")
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            child_path = f"{path}.{key}"
            if key in properties:
                errors.extend(_validate(item, properties[key], child_path))
            elif additional is False:
                errors.append(f"{path}: unexpected property {key!r}")
            elif isinstance(additional, dict):
                errors.extend(_validate(item, additional, child_path))

    return errors


def validate_instance(value, schema, path="$"):
    """Validate an instance after proving that every schema keyword is supported."""
    assert_supported_schema(schema)
    return _validate(value, schema, path)


def validate_document(instance, schema, path="$"):
    return validate_instance(instance, schema, path)


def validate_files(instance_path: Path | str, schema_path: Path | str):
    instance_path = Path(instance_path)
    schema_path = Path(schema_path)
    return validate_document(load_json(instance_path), load_json(schema_path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema", type=Path)
    parser.add_argument("instance", type=Path)
    args = parser.parse_args()
    try:
        errors = validate_files(args.instance, args.schema)
    except (OSError, json.JSONDecodeError, UnsupportedSchemaKeyword) as error:
        print(f"SCHEMA VALIDATION ERROR: {error}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"OK: {args.instance} matches {args.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
