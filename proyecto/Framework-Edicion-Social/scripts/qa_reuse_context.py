#!/usr/bin/env python3
"""Record manual QA dependencies and compare reuse eligibility, never QA approval.

Spec: scope_id, coverage_note and groups containing exactly GROUPS. Group values
are file paths relative to the spec. Engine files must manually inventory runtime
versions, configuration, profile and scripts. This helper hashes listed bytes; it
does not discover omissions or verify declarations inside runtime manifests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from datetime import datetime, timezone


GROUPS = (
    "source", "transcription", "cut_plan", "visual_style", "visual_assets",
    "audio_assets", "mix", "engine",
)
DEPENDENCIES = {
    "visual": ("source", "cut_plan", "visual_style", "visual_assets", "engine"),
    "captions": ("transcription", "cut_plan", "visual_style", "visual_assets", "engine"),
    "audio": ("source", "cut_plan", "audio_assets", "mix", "engine"),
    "semantics": ("source", "transcription", "cut_plan", "visual_style", "visual_assets", "engine"),
}
SHA256 = re.compile(r"^[a-f0-9]{64}$")
LIMITS = (
    "Manual inventory only; unlisted dependencies are not discovered. Hashes "
    "prove local byte integrity, not runtime-manifest claims, QA quality, human "
    "review or approval. Reuse candidates require editorial verification of "
    "coverage and valid prior evidence. Every new MP4 requires exact-export QA."
)


class ContextError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def seal(payload):
    return {**payload, "integrity_digest": digest(payload)}


def read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ContextError(f"cannot read JSON {path}: {error}") from error


def require_fields(value, fields, label):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ContextError(f"{label} fields must be exactly {sorted(fields)}")


def require_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ContextError(f"{label} must be a nonempty string")


def file_record(path):
    path = Path(path).expanduser().resolve()
    try:
        before = path.stat()
        if not path.is_file():
            raise ContextError(f"not a regular file: {path}")
        hashed = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hashed.update(chunk)
        after = path.stat()
    except OSError as error:
        raise ContextError(f"missing or unreadable file {path}: {error}") from error
    identity = lambda stat: (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
    if identity(before) != identity(after):
        raise ContextError(f"file changed while hashing: {path}")
    return {"path": str(path), "bytes": after.st_size, "sha256": hashed.hexdigest()}


def load_spec(path):
    path = Path(path).expanduser().resolve()
    before = file_record(path)
    spec = read_json(path)
    require_fields(spec, {"scope_id", "coverage_note", "groups"}, "spec")
    require_text(spec["scope_id"], "scope_id")
    require_text(spec["coverage_note"], "coverage_note")
    require_fields(spec["groups"], GROUPS, "groups")
    normalized = {}
    for name in GROUPS:
        paths = spec["groups"][name]
        if not isinstance(paths, list) or any(not isinstance(item, str) or not item.strip() for item in paths):
            raise ContextError(f"groups.{name} must be an array of file paths")
        if name in {"source", "engine"} and not paths:
            raise ContextError(f"groups.{name} must not be empty")
        resolved = [str((path.parent / Path(item).expanduser()).resolve()) for item in paths]
        if len(resolved) != len(set(resolved)):
            raise ContextError(f"groups.{name} contains duplicate resolved paths")
        normalized[name] = sorted(resolved)
    if file_record(path) != before:
        raise ContextError(f"spec changed while reading: {path}")
    return before, {"scope_id": spec["scope_id"], "coverage_note": spec["coverage_note"],
                    "groups": normalized}


def snapshot(spec_path):
    spec_record, descriptor = load_spec(spec_path)
    groups = {}
    for name in GROUPS:
        files = [file_record(path) for path in descriptor["groups"][name]]
        groups[name] = {"files": files, "sha256": digest(files)}
    if file_record(spec_record["path"]) != spec_record:
        raise ContextError("spec changed during snapshot")
    return seal({
        "schema_version": "1.0.0", "kind": "qa_reuse_context_snapshot",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scope_id": descriptor["scope_id"], "coverage_note": descriptor["coverage_note"],
        "inventory_scope": "manually_declared_only", "spec": spec_record,
        "spec_descriptor": descriptor, "groups": groups, "limits": LIMITS,
    })


def validate_file_record(record, label):
    require_fields(record, {"path", "bytes", "sha256"}, label)
    if not isinstance(record["path"], str) or not Path(record["path"]).is_absolute():
        raise ContextError(f"{label}.path must be absolute")
    if type(record["bytes"]) is not int or record["bytes"] < 0:
        raise ContextError(f"{label}.bytes must be a nonnegative integer")
    if not isinstance(record["sha256"], str) or not SHA256.fullmatch(record["sha256"]):
        raise ContextError(f"{label}.sha256 is invalid")


def validate_snapshot(value):
    fields = {"schema_version", "kind", "created_at", "scope_id", "coverage_note",
              "inventory_scope", "spec", "spec_descriptor", "groups", "limits", "integrity_digest"}
    require_fields(value, fields, "snapshot")
    if value["schema_version"] != "1.0.0" or value["kind"] != "qa_reuse_context_snapshot":
        raise ContextError("unsupported snapshot contract")
    if value["inventory_scope"] != "manually_declared_only" or value["limits"] != LIMITS:
        raise ContextError("snapshot integrity scope or limits differ")
    require_text(value["scope_id"], "snapshot.scope_id")
    require_text(value["coverage_note"], "snapshot.coverage_note")
    try:
        when = datetime.fromisoformat(value["created_at"])
    except (TypeError, ValueError) as error:
        raise ContextError("snapshot.created_at is invalid") from error
    if when.tzinfo is None:
        raise ContextError("snapshot.created_at needs a timezone")
    payload = {key: item for key, item in value.items() if key != "integrity_digest"}
    if value["integrity_digest"] != digest(payload):
        raise ContextError("snapshot integrity_digest mismatch")
    validate_file_record(value["spec"], "snapshot.spec")
    descriptor = value["spec_descriptor"]
    require_fields(descriptor, {"scope_id", "coverage_note", "groups"}, "spec_descriptor")
    if descriptor["scope_id"] != value["scope_id"] or descriptor["coverage_note"] != value["coverage_note"]:
        raise ContextError("snapshot and descriptor contexts differ")
    require_fields(descriptor["groups"], GROUPS, "spec_descriptor.groups")
    require_fields(value["groups"], GROUPS, "snapshot.groups")
    for name in GROUPS:
        group = value["groups"][name]
        require_fields(group, {"files", "sha256"}, f"snapshot.groups.{name}")
        if not isinstance(group["files"], list):
            raise ContextError(f"snapshot.groups.{name}.files must be an array")
        for record in group["files"]:
            validate_file_record(record, f"snapshot.groups.{name}.files")
        paths = [item["path"] for item in group["files"]]
        if paths != sorted(set(paths)) or paths != descriptor["groups"][name]:
            raise ContextError(f"snapshot.groups.{name} inventory mismatch")
        if name in {"source", "engine"} and not paths:
            raise ContextError(f"snapshot.groups.{name} must not be empty")
        if group["sha256"] != digest(group["files"]):
            raise ContextError(f"snapshot.groups.{name} digest mismatch")
    return value


def compare_snapshots(before_path, after_path, current_spec=None):
    report = {
        "schema_version": "1.0.0", "kind": "qa_reuse_eligibility_comparison",
        "created_at": datetime.now(timezone.utc).isoformat(), "status": "rejected",
        "before_path": str(Path(before_path).expanduser().resolve()),
        "after_path": str(Path(after_path).expanduser().resolve()),
        "current_spec_path": str(Path(current_spec).expanduser().resolve()) if current_spec else None,
        "current_context_verified": False, "scope_id": None,
        "changed_groups": [], "reuse_candidate_scopes": [],
        "rerun_scopes": list(DEPENDENCIES), "scope_reasons": {}, "errors": [],
        "exact_export_qa": "required_for_each_new_mp4", "qa_result": "not_evaluated",
        "approval": "not_evaluated", "limits": LIMITS,
    }
    try:
        before = validate_snapshot(read_json(before_path))
        after = validate_snapshot(read_json(after_path))
        report["scope_id"] = after["scope_id"]
        if before["scope_id"] != after["scope_id"] or before["coverage_note"] != after["coverage_note"]:
            raise ContextError("before and after contexts differ (scope_id or coverage_note)")
        if current_spec is None:
            raise ContextError("--current-spec is required to consider reuse")
        spec_record, descriptor = load_spec(current_spec)
        if spec_record != after["spec"] or descriptor != after["spec_descriptor"]:
            raise ContextError("after snapshot does not match the current spec bytes and descriptor")
        # Only current files are rehashed. Historical before files may legitimately
        # have changed or disappeared since their previous snapshot was made.
        for name in GROUPS:
            for record in after["groups"][name]["files"]:
                if file_record(record["path"]) != record:
                    raise ContextError(f"stale after snapshot: current file changed: {record['path']}")
        if file_record(spec_record["path"]) != spec_record:
            raise ContextError("current spec changed during comparison")
        changed = [name for name in GROUPS if before["groups"][name]["sha256"] != after["groups"][name]["sha256"]]
        report["changed_groups"] = changed
        report["scope_reasons"] = {scope: [name for name in dependencies if name in changed]
                                   for scope, dependencies in DEPENDENCIES.items()}
        report["rerun_scopes"] = [scope for scope, reasons in report["scope_reasons"].items() if reasons]
        report["reuse_candidate_scopes"] = [scope for scope, reasons in report["scope_reasons"].items() if not reasons]
        report["current_context_verified"] = True
        report["status"] = "comparison_complete"
    except (ContextError, OSError, TypeError, ValueError) as error:
        report["errors"].append(str(error))
    return seal(report)


def write_new_json(path, value):
    """Publish a complete file exclusively; neither this call nor a race overwrites."""
    path = Path(path).expanduser().absolute()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    record = commands.add_parser("snapshot", help="hash manually listed dependencies")
    record.add_argument("--spec", type=Path, required=True)
    record.add_argument("--out", type=Path, required=True)
    compare = commands.add_parser("compare", help="consider eligibility; never approve QA")
    compare.add_argument("--before", type=Path, required=True)
    compare.add_argument("--after", type=Path, required=True)
    compare.add_argument("--current-spec", type=Path)
    compare.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = snapshot(args.spec) if args.action == "snapshot" else compare_snapshots(args.before, args.after, args.current_spec)
        write_new_json(args.out, result)
        summary = {"output": str(args.out.absolute()), "kind": result["kind"],
                   "integrity_digest": result["integrity_digest"]}
        if args.action == "compare":
            summary.update({key: result[key] for key in ("status", "reuse_candidate_scopes", "rerun_scopes", "errors")})
        print(json.dumps(summary, ensure_ascii=False))
        return 2 if result.get("status") == "rejected" else 0
    except (ContextError, OSError, TypeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
