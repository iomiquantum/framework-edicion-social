#!/usr/bin/env python3
"""Create fail-closed, delta-only plans from one approved vertical master."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
FRAMEWORK = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from schema_validation import load_json as load_schema_json  # noqa: E402
from schema_validation import validate_document  # noqa: E402


DEFAULT_CATALOG = FRAMEWORK / "platforms/catalog.json"
DEFAULT_DELIVERY_PROFILE = "PLATFORM-INSTAGRAM-REELS-ORGANIC-001"
PROFILE_SCHEMA = FRAMEWORK / "schemas/platform-profile.schema.json"
MASTER_SCHEMA = FRAMEWORK / "schemas/platform-master.schema.json"
ID_FRAGMENT = re.compile(r"[^A-Z0-9-]+")
LOCK_FIELDS = ("take", "cuts", "voice", "semantics", "assets")
MANDATORY_DERIVATIVE_GATES = {
    "explicit_master_approval",
    "content_lock",
    "live_platform_preview",
    "semantic_match",
}


class PlatformPlanError(ValueError):
    """The catalog, master manifest, or requested targets are unsafe or invalid."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path | str, label="JSON"):
    path = Path(path)
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as error:
        raise PlatformPlanError(f"{label} does not exist: {path}") from error
    except json.JSONDecodeError as error:
        raise PlatformPlanError(f"invalid {label} at {path}: {error}") from error


def atomic_write_json(path: Path | str, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise PlatformPlanError(f"refusing to replace symlink output: {path}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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


def document_payload_sha256(document):
    """Hash one JSON document with its binding payload set to null."""
    value = copy.deepcopy(document)
    binding = value.get("binding")
    if not isinstance(binding, dict):
        raise PlatformPlanError("document binding must be an object")
    binding["payload_sha256"] = None
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def seal_document(document):
    value = copy.deepcopy(document)
    value["binding"] = {
        "algorithm": "sha256",
        "canonicalization": "json-sort-keys-utf8-v1",
        "payload_sha256": None,
    }
    value["binding"]["payload_sha256"] = document_payload_sha256(value)
    return value


def verify_document_binding(document, label="document"):
    binding = document.get("binding") if isinstance(document, dict) else None
    if not isinstance(binding, dict) or set(binding) != {
        "algorithm", "canonicalization", "payload_sha256"
    }:
        raise PlatformPlanError(f"{label} has an invalid binding contract")
    if binding.get("algorithm") != "sha256":
        raise PlatformPlanError(f"{label} binding algorithm must be sha256")
    if binding.get("canonicalization") != "json-sort-keys-utf8-v1":
        raise PlatformPlanError(f"{label} binding canonicalization is unsupported")
    if binding.get("payload_sha256") != document_payload_sha256(document):
        raise PlatformPlanError(f"{label} payload SHA-256 does not match")
    return True


def _schema_errors(document, schema_path, label):
    schema = load_schema_json(schema_path)
    errors = validate_document(document, schema)
    if errors:
        joined = "; ".join(errors[:12])
        suffix = f"; plus {len(errors) - 12} more" if len(errors) > 12 else ""
        raise PlatformPlanError(f"{label} does not match schema: {joined}{suffix}")


def _validate_rect(rect, label):
    if rect["x"] + rect["width"] > 1.0000001:
        raise PlatformPlanError(f"{label} extends past the right edge")
    if rect["y"] + rect["height"] > 1.0000001:
        raise PlatformPlanError(f"{label} extends past the bottom edge")


def _validate_machine_constraint(item, profile_id):
    operator = item["operator"]
    number = item["number_value"]
    strings = item["string_values"]
    label = f"{profile_id}.{item['id']}"
    if operator in {"minimum", "maximum"}:
        if number is None or strings:
            raise PlatformPlanError(f"{label}: numeric operator needs number_value only")
    elif operator == "one_of":
        if number is not None or not strings:
            raise PlatformPlanError(f"{label}: one_of needs string_values only")
    elif operator == "equals":
        if (number is None) == (len(strings) == 0):
            raise PlatformPlanError(f"{label}: equals needs exactly one numeric or string value")
        if len(strings) > 1:
            raise PlatformPlanError(f"{label}: equals accepts only one string value")


def validate_profile(profile):
    _schema_errors(profile, PROFILE_SCHEMA, f"profile {profile.get('id', '<unknown>')}")
    profile_id = profile["id"]
    if profile["kind"] == "master" and profile["platform"] != "neutral":
        raise PlatformPlanError(f"{profile_id}: master profile must use platform neutral")
    if profile["kind"] == "derivative" and profile["platform"] == "neutral":
        raise PlatformPlanError(f"{profile_id}: derivative profile cannot use platform neutral")
    zones = profile["internal_defaults"]["safe_zones"]
    for zone_name in ("action", "title", "essential", "captions"):
        _validate_rect(zones[zone_name], f"{profile_id}.safe_zones.{zone_name}")
    for item in zones["exclusions"]:
        _validate_rect(item, f"{profile_id}.safe_zones.exclusions.{item['id']}")
    for constraint in profile["official_constraints"]["automated_constraints"]:
        _validate_machine_constraint(constraint, profile_id)
    required_gates = profile["adaptation_policy"]["required_gates"]
    if profile["kind"] == "derivative" and not MANDATORY_DERIVATIVE_GATES.issubset(
        required_gates
    ):
        missing = sorted(MANDATORY_DERIVATIVE_GATES - set(required_gates))
        raise PlatformPlanError(f"{profile_id}: missing mandatory derivative gates {missing}")
    return profile


def validate_catalog_document(catalog):
    """Validate an already loaded catalog without reopening its source file."""
    expected = {
        "schema_version",
        "catalog_version",
        "updated_at",
        "coordinate_convention",
        "profiles",
    }
    if not isinstance(catalog, dict) or set(catalog) != expected:
        raise PlatformPlanError(f"platform catalog fields must be exactly {sorted(expected)}")
    if catalog["schema_version"] != "1.0.0":
        raise PlatformPlanError("unsupported platform catalog schema_version")
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", catalog["catalog_version"]):
        raise PlatformPlanError("invalid platform catalog_version")
    try:
        date.fromisoformat(catalog["updated_at"])
    except (TypeError, ValueError) as error:
        raise PlatformPlanError("platform catalog updated_at must be an ISO date") from error
    if not isinstance(catalog["coordinate_convention"], str) or not catalog["coordinate_convention"]:
        raise PlatformPlanError("platform catalog coordinate_convention must be non-empty")
    if not isinstance(catalog["profiles"], list) or not catalog["profiles"]:
        raise PlatformPlanError("platform catalog must contain profiles")
    ids = []
    surfaces = []
    for profile in catalog["profiles"]:
        validate_profile(profile)
        ids.append(profile["id"])
        surfaces.append((profile["platform"], profile["surface"]))
    if len(ids) != len(set(ids)):
        raise PlatformPlanError("platform profile ids must be unique")
    if len(surfaces) != len(set(surfaces)):
        raise PlatformPlanError("platform/surface pairs must be unique")
    masters = [profile for profile in catalog["profiles"] if profile["kind"] == "master"]
    if len(masters) != 1:
        raise PlatformPlanError("platform catalog must contain exactly one master profile")
    return catalog


def load_catalog(path: Path | str = DEFAULT_CATALOG):
    path = Path(path)
    return validate_catalog_document(read_json(path, "platform catalog"))


def validate_master(master, catalog):
    _schema_errors(master, MASTER_SCHEMA, "platform master")
    by_id = {profile["id"]: profile for profile in catalog["profiles"]}
    profile = by_id.get(master["profile_id"])
    if profile is None:
        raise PlatformPlanError(f"master references unknown profile {master['profile_id']}")
    if profile["kind"] != "master":
        raise PlatformPlanError("master manifest must reference a master profile")

    defaults = profile["internal_defaults"]
    technical = master["technical"]
    expected_values = {
        "width": defaults["canvas"]["width"],
        "height": defaults["canvas"]["height"],
        "aspect_ratio": defaults["canvas"]["aspect_ratio"],
        "container": defaults["video"]["container"],
        "video_codec": defaults["video"]["codec"],
        "pixel_format": defaults["video"]["pixel_format"],
        "audio_codec": defaults["audio"]["codec"],
        "audio_sample_rate_hz": defaults["audio"]["sample_rate_hz"],
        "color_space": defaults["video"]["color_space"],
    }
    mismatches = [
        f"{field}={technical[field]!r} (expected {expected!r})"
        for field, expected in expected_values.items()
        if str(technical[field]).lower() != str(expected).lower()
    ]
    if abs(float(technical["fps"]) - float(defaults["canvas"]["fps"])) > 0.01:
        mismatches.append(
            f"fps={technical['fps']!r} (expected {defaults['canvas']['fps']!r})"
        )
    duration = technical["duration_seconds"]
    duration_defaults = defaults["duration"]
    if not duration_defaults["workflow_min_seconds"] <= duration <= duration_defaults["workflow_max_seconds"]:
        mismatches.append(
            "duration_seconds outside the master workflow range "
            f"{duration_defaults['workflow_min_seconds']}..{duration_defaults['workflow_max_seconds']}"
        )
    if mismatches:
        raise PlatformPlanError("master technical profile mismatch: " + "; ".join(mismatches))

    approval = master["approval"]
    if approval["status"] == "approved":
        if not approval["explicit_user_approval"]:
            raise PlatformPlanError("approved master must record explicit_user_approval=true")
        if not approval["approved_by"] or not approval["approved_at"]:
            raise PlatformPlanError("approved master must record approved_by and approved_at")
    elif approval["explicit_user_approval"]:
        raise PlatformPlanError("explicit_user_approval cannot be true unless status is approved")

    lock = master["content_lock"]
    all_locked = all(lock[field] for field in LOCK_FIELDS)
    if lock["status"] == "locked" and (not all_locked or not lock["locked_at"]):
        raise PlatformPlanError("locked content requires every lock flag and locked_at")
    if lock["status"] == "unlocked" and all_locked:
        raise PlatformPlanError("content lock status is unlocked although every lock flag is true")
    return profile


def approval_is_ready(master):
    approval = master["approval"]
    return bool(
        approval["status"] == "approved"
        and approval["explicit_user_approval"]
        and approval["approved_by"]
        and approval["approved_at"]
    )


def content_lock_is_ready(master):
    lock = master["content_lock"]
    hashes = master["hashes"]
    return bool(
        lock["status"] == "locked"
        and lock["locked_at"]
        and all(lock[field] for field in LOCK_FIELDS)
        and all(hashes[field] for field in hashes)
    )


def _parse_targets(values):
    if not values:
        return []
    result = []
    for value in values:
        result.extend(item.strip() for item in value.split(",") if item.strip())
    return list(dict.fromkeys(result))


def _slug(value):
    value = ID_FRAGMENT.sub("-", value.upper()).strip("-")
    if not value:
        raise PlatformPlanError("cannot make adaptation id from an empty master id")
    return value


def _clean_path(value, label):
    if not isinstance(value, (str, os.PathLike)):
        raise PlatformPlanError(f"{label} must be a string or path")
    raw = os.fspath(value)
    if not isinstance(raw, str) or not raw.strip():
        raise PlatformPlanError(f"{label} cannot be empty")
    if "\x00" in raw:
        raise PlatformPlanError(f"{label} cannot contain a NUL byte")
    if any(part in {".", ".."} for part in raw.replace("\\", "/").split("/")):
        raise PlatformPlanError(f"{label} cannot contain . or .. path segments")
    return raw


def _profile_target(profile, master, plan_ready, output_dir):
    defaults = profile["internal_defaults"]
    safe = defaults["safe_zones"]
    essential = safe["essential"]
    captions = safe["captions"]
    approval = master["approval"]
    lock = master["content_lock"]
    approval_ready = approval_is_ready(master)
    lock_ready = content_lock_is_ready(master)
    gate_status = "passed" if approval_ready else "pending"
    lock_gate_status = "passed" if lock_ready else "pending"
    output_name = f"{master['video_id']}-{profile['surface'].replace('_', '-')}.mp4"
    output_path = Path(output_dir) / profile["platform"] / output_name
    known_gates = {
        "explicit_master_approval": {
            "id": "explicit_master_approval",
            "status": gate_status,
            "evidence": (
                f"{approval['approved_by']} @ {approval['approved_at']}"
                if approval_ready
                else None
            ),
            "note": "Debe existir aprobacion humana explicita del master.",
        },
        "content_lock": {
            "id": "content_lock",
            "status": lock_gate_status,
            "evidence": lock["locked_at"] if lock_ready else None,
            "note": "Toma, cortes, voz, semantica, assets y hashes deben estar bloqueados.",
        },
        "live_platform_preview": {
            "id": "live_platform_preview",
            "status": "pending",
            "evidence": None,
            "note": "Las coordenadas son internas; comprobar la interfaz real antes del render final.",
        },
        "semantic_match": {
            "id": "semantic_match",
            "status": "pending",
            "evidence": None,
            "note": "Confirmar que CTA y reflujo mantienen significado, ritmo y assets aprobados.",
        },
    }
    required_gates = list(profile["adaptation_policy"]["required_gates"])
    gates = [
        copy.deepcopy(
            known_gates.get(
                gate_id,
                {
                    "id": gate_id,
                    "status": "pending",
                    "evidence": None,
                    "note": f"Gate requerido por el perfil {profile['id']}; adjuntar evidencia.",
                },
            )
        )
        for gate_id in required_gates
    ]
    return {
        "profile_id": profile["id"],
        "platform": profile["platform"],
        "surface": profile["surface"],
        "status": "ready_for_preview" if plan_ready else "blocked",
        "delta": {
            "layout": f"Refluir elementos al token {defaults['layout']['token']} sin modificar cortes.",
            "captions": "Cambiar solo saltos de linea y posicion; conservar el texto aprobado.",
            "cta": "Usar wording nativo solo si es semanticamente equivalente y aprobarlo en preview.",
            "export": "Aplicar el preset tecnico del perfil sin rearmar el montaje.",
            "semantic_guard": "Cualquier cambio de mensaje, claim, toma, timing o asset devuelve el trabajo a aprobacion del master.",
        },
        "safe_zone": {
            "provenance": safe["provenance"],
            "requires_live_preview": safe["requires_live_preview"],
            "essential": dict(essential),
            "captions": dict(captions),
        },
        "export": {
            "width": defaults["canvas"]["width"],
            "height": defaults["canvas"]["height"],
            "fps": defaults["canvas"]["fps"],
            "container": defaults["video"]["container"],
            "video_codec": defaults["video"]["codec"],
            "pixel_format": defaults["video"]["pixel_format"],
            "target_bitrate_mbps": defaults["video"]["target_bitrate_mbps"],
            "audio_codec": defaults["audio"]["codec"],
            "audio_sample_rate_hz": defaults["audio"]["sample_rate_hz"],
            "color_space": defaults["video"]["color_space"],
        },
        "hyperframes_variables": {
            "platform_profile": profile["id"],
            "layout_token": defaults["layout"]["token"],
            "cta_token": defaults["cta"]["token"],
            "safe_essential_x": essential["x"],
            "safe_essential_y": essential["y"],
            "safe_essential_width": essential["width"],
            "safe_essential_height": essential["height"],
            "caption_safe_x": captions["x"],
            "caption_safe_y": captions["y"],
            "caption_safe_width": captions["width"],
            "caption_safe_height": captions["height"],
        },
        "required_gates": required_gates,
        "gates": gates,
        "output_path": output_path.as_posix(),
    }


def build_plan(master, catalog, target_ids=None, master_path="platform-master.json", catalog_path=DEFAULT_CATALOG, output_dir="deliveries"):
    master_path = _clean_path(master_path, "master manifest path")
    catalog_path = _clean_path(catalog_path, "catalog path")
    output_dir = _clean_path(output_dir, "derivative output directory")
    master_profile = validate_master(master, catalog)
    by_id = {profile["id"]: profile for profile in catalog["profiles"]}
    available = [
        profile
        for profile in catalog["profiles"]
        if profile["kind"] == "derivative" and profile["status"] == "active"
    ]
    # Resource policy: one Instagram Reels master is the universal social
    # delivery by default. Extra platform renders must be explicitly requested
    # after a material delta has been identified and documented by the caller.
    requested = list(target_ids or [DEFAULT_DELIVERY_PROFILE])
    if not requested:
        raise PlatformPlanError("at least one derivative target is required")
    if len(requested) != len(set(requested)):
        raise PlatformPlanError("target profile ids must be unique")
    targets = []
    for profile_id in requested:
        profile = by_id.get(profile_id)
        if profile is None:
            raise PlatformPlanError(f"unknown target profile {profile_id}")
        if profile["kind"] != "derivative" or profile["status"] != "active":
            raise PlatformPlanError(f"target {profile_id} is not an active derivative profile")
        targets.append(profile)

    approval_ready = approval_is_ready(master)
    lock_ready = content_lock_is_ready(master)
    reasons = []
    if not approval_ready:
        reasons.append("El master no tiene aprobacion explicita del usuario.")
    if not lock_ready:
        reasons.append("El contenido o sus hashes no estan completamente bloqueados.")
    if not approval_ready:
        status = "blocked_until_master_approved"
    elif not lock_ready:
        status = "blocked_until_content_locked"
    else:
        status = "ready_for_platform_preview"
    plan_ready = status == "ready_for_platform_preview"

    plan = {
        "schema_version": "1.1.0",
        "adaptation_id": f"ADAPT-{_slug(master['master_id'])}",
        "generated_at": utc_now(),
        "output_root": output_dir,
        "master": {
            "master_id": master["master_id"],
            "manifest_path": master_path,
            "profile_id": master["profile_id"],
            "approval_status": master["approval"]["status"],
            "explicit_user_approval": master["approval"]["explicit_user_approval"],
            "content_lock_status": master["content_lock"]["status"],
        },
        "catalog": {
            "path": catalog_path,
            "catalog_version": catalog["catalog_version"],
        },
        "status": status,
        "blocking_reasons": reasons,
        "policy": {
            "strategy": "instagram_master_reuse_unless_material_delta",
            "preserve": list(master_profile["adaptation_policy"]["preserve"]),
            "allowed_changes": list(master_profile["adaptation_policy"]["may_change"]),
            "prohibited_changes": list(
                master_profile["adaptation_policy"]["never_change_without_new_approval"]
            ),
        },
        "targets": [
            _profile_target(profile, master, plan_ready, output_dir) for profile in targets
        ],
    }
    return seal_document(plan)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, required=True, help="platform-master manifest")
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument(
        "--target",
        action="append",
        help=(
            "profile id or comma-separated ids; defaults only to Instagram Reels. "
            "Add TikTok or Shorts only after documenting a material platform delta."
        ),
    )
    parser.add_argument("--output-dir", default="deliveries")
    parser.add_argument("--out", type=Path, required=True)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        catalog = load_catalog(args.catalog)
        master = read_json(args.master, "platform master")
        plan = build_plan(
            master,
            catalog,
            target_ids=_parse_targets(args.target),
            master_path=args.master,
            catalog_path=args.catalog,
            output_dir=args.output_dir,
        )
        atomic_write_json(args.out, plan)
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        if plan["status"] != "ready_for_platform_preview":
            print(
                f"BLOCKED: {plan['status']}; plan saved but derivatives are not ready",
                file=sys.stderr,
            )
            return 3
        return 0
    except (PlatformPlanError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
