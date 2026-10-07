#!/usr/bin/env python3
"""Compute transitively invalidated production layers and artifacts."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


IDENTIFIER = re.compile(r"^[a-z][a-z0-9_-]*$")


class DependencyMapError(ValueError):
    pass


def read_json(path):
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as error:
        raise DependencyMapError(f"invalid dependency-map JSON: {error}") from error


def atomic_write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def validate_dependency_map(document):
    if not isinstance(document, dict):
        raise DependencyMapError("dependency map must be an object")
    required = {"schema_version", "project_id", "inputs", "layers"}
    if set(document) != required:
        raise DependencyMapError(f"dependency map fields must be exactly {sorted(required)}")
    if document["schema_version"] != "1.0.0":
        raise DependencyMapError("unsupported dependency-map schema_version")
    if not isinstance(document["project_id"], str):
        raise DependencyMapError("project_id must be a string")
    if not isinstance(document["inputs"], list) or not isinstance(document["layers"], list):
        raise DependencyMapError("inputs and layers must be arrays")

    input_ids = []
    for index, item in enumerate(document["inputs"]):
        if not isinstance(item, dict) or set(item) != {"id", "description"}:
            raise DependencyMapError(f"inputs[{index}] must contain id and description")
        if not isinstance(item["id"], str) or not IDENTIFIER.fullmatch(item["id"]):
            raise DependencyMapError(f"inputs[{index}].id is invalid")
        if not isinstance(item["description"], str):
            raise DependencyMapError(f"inputs[{index}].description must be a string")
        input_ids.append(item["id"])
    if len(input_ids) != len(set(input_ids)):
        raise DependencyMapError("input ids must be unique")

    layer_ids = []
    artifact_ids = set()
    for index, layer in enumerate(document["layers"]):
        expected = {"id", "description", "depends_on", "heavy", "artifacts"}
        if not isinstance(layer, dict) or set(layer) != expected:
            raise DependencyMapError(f"layers[{index}] fields must be exactly {sorted(expected)}")
        layer_id = layer["id"]
        if not isinstance(layer_id, str) or not IDENTIFIER.fullmatch(layer_id):
            raise DependencyMapError(f"layers[{index}].id is invalid")
        if not isinstance(layer["description"], str):
            raise DependencyMapError(f"layers[{index}].description must be a string")
        if not isinstance(layer["heavy"], bool):
            raise DependencyMapError(f"layers[{index}].heavy must be boolean")
        if not isinstance(layer["depends_on"], list) or not all(isinstance(item, str) for item in layer["depends_on"]):
            raise DependencyMapError(f"layers[{index}].depends_on must be an array of ids")
        if len(layer["depends_on"]) != len(set(layer["depends_on"])):
            raise DependencyMapError(f"layers[{index}].depends_on contains duplicates")
        if not isinstance(layer["artifacts"], list):
            raise DependencyMapError(f"layers[{index}].artifacts must be an array")
        for artifact_index, artifact in enumerate(layer["artifacts"]):
            fields = {"id", "path", "kind"}
            if not isinstance(artifact, dict) or set(artifact) != fields:
                raise DependencyMapError(
                    f"layers[{index}].artifacts[{artifact_index}] fields must be exactly {sorted(fields)}"
                )
            if not isinstance(artifact["id"], str) or not IDENTIFIER.fullmatch(artifact["id"]):
                raise DependencyMapError(f"invalid artifact id in layer {layer_id}")
            if artifact["id"] in artifact_ids:
                raise DependencyMapError(f"duplicate artifact id {artifact['id']}")
            artifact_ids.add(artifact["id"])
            if not isinstance(artifact["path"], str) or not artifact["path"]:
                raise DependencyMapError(f"artifact {artifact['id']} path must be non-empty")
            if artifact["kind"] not in {"file", "directory", "logical"}:
                raise DependencyMapError(f"artifact {artifact['id']} has invalid kind")
        layer_ids.append(layer_id)

    if len(layer_ids) != len(set(layer_ids)):
        raise DependencyMapError("layer ids must be unique")
    overlap = sorted(set(input_ids) & set(layer_ids))
    if overlap:
        raise DependencyMapError(f"ids cannot be both input and layer: {', '.join(overlap)}")

    known = set(input_ids) | set(layer_ids)
    by_id = {layer["id"]: layer for layer in document["layers"]}
    for layer in document["layers"]:
        for dependency in layer["depends_on"]:
            if dependency not in known:
                raise DependencyMapError(f"layer {layer['id']} references unknown dependency {dependency}")
            if dependency == layer["id"]:
                raise DependencyMapError(f"layer {layer['id']} cannot depend on itself")

    visiting = set()
    visited = set()

    def visit(layer_id, trail):
        if layer_id in visiting:
            cycle = " -> ".join([*trail, layer_id])
            raise DependencyMapError(f"dependency cycle: {cycle}")
        if layer_id in visited:
            return
        visiting.add(layer_id)
        for dependency in by_id[layer_id]["depends_on"]:
            if dependency in by_id:
                visit(dependency, [*trail, layer_id])
        visiting.remove(layer_id)
        visited.add(layer_id)

    for layer_id in layer_ids:
        visit(layer_id, [])
    return document


def calculate_impact(document, changed):
    validate_dependency_map(document)
    changed = list(dict.fromkeys(changed))
    known = {item["id"] for item in document["inputs"]} | {item["id"] for item in document["layers"]}
    unknown = sorted(set(changed) - known)
    if unknown:
        raise DependencyMapError(f"unknown changed ids: {', '.join(unknown)}")
    if not changed:
        raise DependencyMapError("at least one changed input or layer is required")

    invalidated = {item for item in changed if item in {layer["id"] for layer in document["layers"]}}
    reasons = {item: {item} for item in invalidated}
    changed_set = set(changed)
    progress = True
    while progress:
        progress = False
        for layer in document["layers"]:
            dependencies = set(layer["depends_on"])
            triggers = dependencies & (changed_set | invalidated)
            if triggers and layer["id"] not in invalidated:
                invalidated.add(layer["id"])
                progress = True
            if triggers:
                direct_reasons = set()
                for trigger in triggers:
                    direct_reasons.update(reasons.get(trigger, {trigger}))
                reasons.setdefault(layer["id"], set()).update(direct_reasons)

    invalidated_layers = []
    artifacts = []
    heavy_layers = []
    for layer in document["layers"]:
        if layer["id"] not in invalidated:
            continue
        invalidated_layers.append(
            {
                "id": layer["id"],
                "heavy": layer["heavy"],
                "invalidated_by": sorted(reasons.get(layer["id"], changed_set)),
            }
        )
        if layer["heavy"]:
            heavy_layers.append(layer["id"])
        for artifact in layer["artifacts"]:
            artifacts.append({**artifact, "layer_id": layer["id"]})

    return {
        "schema_version": "1.0.0",
        "project_id": document["project_id"],
        "changed": changed,
        "invalidated_layers": invalidated_layers,
        "invalidated_artifacts": artifacts,
        "heavy_layers": heavy_layers,
        "unaffected_layers": [
            layer["id"] for layer in document["layers"] if layer["id"] not in invalidated
        ],
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }


def parse_changed(values):
    result = []
    for value in values:
        result.extend(item.strip() for item in value.split(",") if item.strip())
    return list(dict.fromkeys(result))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", dest="map_path", type=Path, required=True)
    parser.add_argument("--changed", action="append", required=True, help="id or comma-separated ids")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    try:
        result = calculate_impact(read_json(args.map_path), parse_changed(args.changed))
        if args.out:
            atomic_write_json(args.out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (DependencyMapError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
