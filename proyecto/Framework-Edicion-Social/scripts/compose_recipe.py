#!/usr/bin/env python3
"""Compile up to three contextual, modular creative recipes for a video.

The compiler is intentionally a proposal engine, not an autonomous creative
director. It combines one module from each of six axes, rejects incompatible
combinations, accounts for recent repetition and available asset types, and
returns a deterministic review order. It never crowns a universal winner and
never promotes a recipe from performance or approval evidence automatically.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import itertools
import json
import math
import os
import re
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

from schema_validation import assert_supported_schema, validate_document


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent.resolve()
SCHEMA_DIR = ROOT / "schemas"
DEFAULT_CATALOG = ROOT / "creative-recipes" / "catalog.json"
BLUEPRINT_SCHEMA = SCHEMA_DIR / "creative-blueprint.schema.json"
CATALOG_SCHEMA = SCHEMA_DIR / "creative-recipe-catalog.schema.json"
PLAN_SCHEMA = SCHEMA_DIR / "creative-recipe-plan.schema.json"
SERIES_CONTRACT_SCHEMA = SCHEMA_DIR / "series-contract.schema.json"
SERIES_LEDGER_SCHEMA = SCHEMA_DIR / "series-variety-ledger.schema.json"
ASSET_INDEX_SCHEMA = SCHEMA_DIR / "asset-index.schema.json"

GENERATOR_VERSION = "creative-recipe-compose-v1"
KINDS = ("hook", "structure", "visual_system", "motion", "sound", "cta")
PREFIX_BY_KIND = {
    "hook": "HOOK-",
    "structure": "STRUCT-",
    "visual_system": "VIS-",
    "motion": "MOTION-",
    "sound": "SOUND-",
    "cta": "CTA-",
}
OPTION_IDS = ("OPTION-A", "OPTION-B", "OPTION-C")
ACTIVE_STATUSES = {"candidate", "testing", "approved"}
BAD_ASSET_STATUSES = {"rejected", "deprecated", "blocked", "deleted", "missing"}
ASSET_TYPE_ALIASES = {
    "img": "image",
    "photo": "image",
    "photograph": "image",
    "illustration": "image",
    "broll": "image",
    "b_roll": "image",
    "visual": "image",
    "svg": "icon",
    "vector": "icon",
    "sound_effect": "sfx",
    "soundeffect": "sfx",
    "effect": "sfx",
    "bgm": "music",
    "music_bed": "music",
    "alpha_video": "cutout",
    "transparent_video": "cutout",
    "graphic": "typographic_overlay",
    "text_overlay": "typographic_overlay",
}


class CreativeRecipeError(ValueError):
    """A user-facing catalog, input, path, or output contract error."""


def _confined_path(
    path: Path | str,
    *,
    must_exist: bool = True,
    expect: str | None = None,
) -> Path:
    """Resolve a traversal-free, non-symlink path inside the workspace."""
    raw = Path(path).expanduser()
    if ".." in raw.parts:
        raise CreativeRecipeError(f"Path traversal is not allowed: {path}")
    candidate = raw if raw.is_absolute() else Path.cwd() / raw
    lexical = Path(os.path.abspath(candidate))
    try:
        relative = lexical.relative_to(WORKSPACE_ROOT)
    except ValueError as error:
        raise CreativeRecipeError(f"Path is outside the workspace: {path}") from error

    current = WORKSPACE_ROOT
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise CreativeRecipeError(f"Symlink paths are not allowed: {current}")
        if not current.exists():
            break

    resolved = lexical.resolve(strict=must_exist)
    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError as error:
        raise CreativeRecipeError(f"Resolved path escapes the workspace: {path}") from error
    if expect == "file":
        wrong = not resolved.is_file() if must_exist else resolved.exists() and not resolved.is_file()
        if wrong:
            raise CreativeRecipeError(f"Expected a file path: {path}")
    if expect == "dir":
        wrong = not resolved.is_dir() if must_exist else resolved.exists() and not resolved.is_dir()
        if wrong:
            raise CreativeRecipeError(f"Expected a directory path: {path}")
    return resolved


def _portable_path(path: Path | str) -> str:
    resolved = _confined_path(path, must_exist=True, expect="file")
    return resolved.relative_to(WORKSPACE_ROOT).as_posix()


def load_json(path: Path | str) -> dict[str, Any]:
    source = _confined_path(path, must_exist=True, expect="file")
    try:
        with source.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except json.JSONDecodeError as error:
        raise CreativeRecipeError(f"Invalid JSON in {source}: {error}") from error
    if not isinstance(value, dict):
        raise CreativeRecipeError(f"Expected a JSON object: {source}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_sha256(path: Path | str) -> str:
    source = _confined_path(path, must_exist=True, expect="file")
    digest = hashlib.sha256()
    before = source.stat()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    after = source.stat()
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if identity_before != identity_after:
        raise CreativeRecipeError(f"Input changed while hashing: {source}")
    return digest.hexdigest()


def _write_json(
    path: Path | str,
    document: dict[str, Any],
    *,
    protected_paths: tuple[Path | str, ...] = (),
) -> None:
    target = _confined_path(path, must_exist=False, expect="file")
    for protected in protected_paths:
        protected_path = _confined_path(protected, must_exist=True, expect="file")
        if target == protected_path:
            raise CreativeRecipeError(f"Output may not overwrite an input: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target = _confined_path(target, must_exist=False, expect="file")
    payload = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    temporary_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
            temporary_name = handle.name
        os.replace(temporary_name, target)
    except Exception:
        if temporary_name:
            Path(temporary_name).unlink(missing_ok=True)
        raise


def _validate_schema(document: dict[str, Any], schema_path: Path, label: str) -> None:
    schema = load_json(schema_path)
    assert_supported_schema(schema)
    errors = validate_document(document, schema)
    if errors:
        detail = "\n  - ".join(errors)
        raise CreativeRecipeError(f"{label} does not match {schema_path.name}:\n  - {detail}")


def normalize_token(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value).strip().lower())
    text = "".join(character for character in text if not unicodedata.combining(character))
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def _normalized(values: Any) -> set[str]:
    if not isinstance(values, list):
        return set()
    return {token for value in values if (token := normalize_token(value))}


def _unique(values: list[str] | tuple[str, ...]) -> list[str]:
    return sorted({value for value in values if value})


def validate_catalog(catalog: dict[str, Any]) -> None:
    _validate_schema(catalog, CATALOG_SCHEMA, "Creative recipe catalog")
    policy = catalog["policy"]
    if policy["fatigue_notice_occurrences"] > policy["fatigue_warning_occurrences"]:
        raise CreativeRecipeError("fatigue notice threshold cannot exceed warning threshold")
    if not math.isclose(sum(catalog["kind_weights"].values()), 1.0, abs_tol=1e-9):
        raise CreativeRecipeError("kind_weights must sum to exactly 1.0")

    modules = catalog["modules"]
    ids = [module["id"] for module in modules]
    if len(ids) != len(set(ids)):
        raise CreativeRecipeError("Creative recipe module ids must be unique")
    by_id = {module["id"]: module for module in modules}
    for kind in KINDS:
        if not any(module["kind"] == kind and module["status"] in ACTIVE_STATUSES for module in modules):
            raise CreativeRecipeError(f"Catalog has no active module for kind {kind}")

    for module in modules:
        if not module["id"].startswith(PREFIX_BY_KIND[module["kind"]]):
            raise CreativeRecipeError(
                f"Module {module['id']} prefix does not match kind {module['kind']}"
            )
        if module["duration_min_s"] > module["duration_max_s"]:
            raise CreativeRecipeError(f"Module {module['id']} has an inverted duration range")
        if module["effort"]["minutes_min"] > module["effort"]["minutes_max"]:
            raise CreativeRecipeError(f"Module {module['id']} has an inverted effort range")
        references = module["requires_any_modules"] + module["incompatible_with"]
        unknown = sorted(set(references) - set(by_id))
        if unknown:
            raise CreativeRecipeError(f"Module {module['id']} references unknown modules: {unknown}")
        if module["id"] in references:
            raise CreativeRecipeError(f"Module {module['id']} may not reference itself")
        for incompatible_id in module["incompatible_with"]:
            if module["id"] not in by_id[incompatible_id]["incompatible_with"]:
                raise CreativeRecipeError(
                    f"Incompatibility must be symmetric: {module['id']} / {incompatible_id}"
                )


def validate_blueprint(blueprint: dict[str, Any]) -> None:
    _validate_schema(blueprint, BLUEPRINT_SCHEMA, "Creative blueprint")
    beat_ids = [beat["id"] for beat in blueprint["beats"]]
    if len(beat_ids) != len(set(beat_ids)):
        raise CreativeRecipeError("Blueprint beat ids must be unique")
    if blueprint["emotion_arc"]["peak_beat_id"] not in beat_ids:
        raise CreativeRecipeError("Blueprint peak_beat_id does not exist in beats")


def _validate_optional_inputs(
    series_contract: dict[str, Any] | None,
    series_memory: dict[str, Any] | None,
    asset_index: dict[str, Any] | None,
) -> None:
    if series_contract is not None:
        _validate_schema(series_contract, SERIES_CONTRACT_SCHEMA, "Series contract")
        family_policy = series_contract.get("family_policy", {})
        if family_policy.get("single_global_winner") is not False:
            raise CreativeRecipeError("Series contract must keep single_global_winner=false")
        if family_policy.get("preserve_multiple_families") is not True:
            raise CreativeRecipeError("Series contract must preserve multiple creative families")
    if series_memory is not None:
        if not isinstance(series_memory, dict):
            raise CreativeRecipeError("Series memory must be a JSON object")
        _validate_schema(series_memory, SERIES_LEDGER_SCHEMA, "Series variety ledger")
    if asset_index is not None and not isinstance(asset_index, dict):
        raise CreativeRecipeError("Asset index must be a JSON object")
    if asset_index is not None:
        _validate_schema(asset_index, ASSET_INDEX_SCHEMA, "Semantic asset index")


def _context_from_blueprint(blueprint: dict[str, Any]) -> dict[str, Any]:
    signals = blueprint["style_selection_signals"]
    normalized_signals = {name: _normalized(values) for name, values in signals.items()}
    context_tags = set().union(*normalized_signals.values())
    aliases = {
        "technology": {"tech"},
        "tech": {"technology"},
        "process_explanation": {"education", "tutorial"},
        "full_length_reel": {"short_form_vertical"},
        "high_contrast_editorial": {"authority"},
    }
    for tag in list(context_tags):
        context_tags.update(aliases.get(tag, set()))
    roles = {normalize_token(beat["narrative_role"]) for beat in blueprint["beats"]}
    visual_roles = {
        normalize_token(role)
        for beat in blueprint["beats"]
        for role in beat.get("visual_roles", [])
    }
    energies = [float(beat["energy"]) for beat in blueprint["beats"]]
    average_energy = sum(energies) / len(energies)
    categories_present = sum(bool(values) for values in normalized_signals.values())
    signal_count = sum(len(values) for values in normalized_signals.values())
    return {
        "signals": normalized_signals,
        "tags": context_tags,
        "hook_pattern": normalize_token(blueprint["hook"]["pattern"]),
        "roles": roles,
        "visual_roles": visual_roles,
        "source_geometries": normalized_signals["source_geometry"],
        "platform_fit": normalized_signals["platform_fit"],
        "duration_s": float(blueprint["duration_target_s"]),
        "average_energy": average_energy,
        "categories_present": categories_present,
        "signal_count": signal_count,
    }


def _dimension_score(
    wanted: set[str],
    observed: set[str],
    *,
    miss_score: float = 0.08,
    denominator_cap: int = 2,
) -> tuple[float, list[str]]:
    if not wanted:
        return 0.0, []
    matches = sorted(wanted & observed)
    if not matches:
        return miss_score, []
    denominator = max(1, min(denominator_cap, len(wanted)))
    return min(1.0, len(matches) / denominator), matches


def _score_module(module: dict[str, Any], context: dict[str, Any]) -> dict[str, Any] | None:
    if module["status"] not in ACTIVE_STATUSES:
        return None
    duration = context["duration_s"]
    if duration < module["duration_min_s"] or duration > module["duration_max_s"]:
        return None
    avoid_hits = sorted(_normalized(module["avoid_for"]) & context["tags"])
    if avoid_hits:
        return None
    if not module["design_contract"]["face_safe"]:
        return None

    components: list[tuple[str, float, float, list[str]]] = []
    best_score, best_hits = _dimension_score(_normalized(module["best_for"]), context["tags"])
    components.append(("context", 0.32, best_score, best_hits))

    hook_patterns = _normalized(module["hook_patterns"])
    if hook_patterns:
        hook_match = context["hook_pattern"] in hook_patterns
        components.append(
            ("hook_pattern", 0.16, 1.0 if hook_match else 0.18, [context["hook_pattern"]] if hook_match else [])
        )
    narrative_score, narrative_hits = _dimension_score(
        _normalized(module["narrative_roles"]), context["roles"], denominator_cap=2
    )
    if module["narrative_roles"]:
        components.append(("narrative_roles", 0.14, narrative_score, narrative_hits))
    geometry_score, geometry_hits = _dimension_score(
        _normalized(module["source_geometries"]), context["source_geometries"], denominator_cap=1
    )
    if module["source_geometries"]:
        components.append(("source_geometry", 0.12, geometry_score, geometry_hits))
    platform_score, platform_hits = _dimension_score(
        _normalized(module["platform_fit"]), context["platform_fit"], denominator_cap=1
    )
    if module["platform_fit"]:
        components.append(("platform_fit", 0.1, platform_score, platform_hits))

    energy_score = max(0.0, 1.0 - abs(context["average_energy"] - module["energy_target"]) / 0.8)
    components.append(("energy", 0.1, energy_score, []))
    components.append(("duration", 0.06, 1.0, []))

    weight_total = sum(weight for _, weight, _, _ in components)
    score = sum(weight * value for _, weight, value, _ in components) / weight_total
    positives: list[str] = []
    negatives: list[str] = []
    for name, _, value, matches in components:
        positives.extend(f"{name}:{match}" for match in matches)
        if name == "energy":
            positives.append(f"energy_fit:{value:.3f}")
        elif name == "duration":
            positives.append(f"duration:{duration:g}s")
        elif value < 0.2 and not matches:
            negatives.append(f"{name}:no_match")
    return {
        "module": module,
        "fit_score": round(max(0.0, min(1.0, score)), 6),
        "positive_matches": _unique(positives),
        "negative_matches": _unique(negatives),
    }


def _combination_conflicts(modules: tuple[dict[str, Any], ...]) -> list[str]:
    ids = {module["id"] for module in modules}
    conflicts: list[str] = []
    for module in modules:
        incompatible = sorted(ids & set(module["incompatible_with"]))
        for other in incompatible:
            pair = " / ".join(sorted((module["id"], other)))
            conflicts.append(f"incompatible:{pair}")
        required = module["requires_any_modules"]
        if required and not ids.intersection(required):
            conflicts.append(
                f"requires_any:{module['id']} needs one of {','.join(sorted(required))}"
            )
    return _unique(conflicts)


def _walk_strings(value: Any) -> set[str]:
    tokens: set[str] = set()
    if isinstance(value, str):
        normalized = normalize_token(value)
        if normalized:
            tokens.add(normalized)
    elif isinstance(value, dict):
        for child in value.values():
            tokens.update(_walk_strings(child))
    elif isinstance(value, list):
        for child in value:
            tokens.update(_walk_strings(child))
    return tokens


def _memory_entries(series_memory: dict[str, Any] | None, window: int) -> list[dict[str, Any]]:
    if series_memory is None:
        return []
    candidates = series_memory.get("entries")
    if not isinstance(candidates, list):
        return []
    entries = [entry for entry in candidates if isinstance(entry, dict)]
    return entries[-window:]


def _fatigue_report(
    modules: tuple[dict[str, Any], ...],
    series_memory: dict[str, Any] | None,
    policy: dict[str, Any],
) -> dict[str, Any]:
    memory_window = None
    if series_memory is not None:
        candidate = series_memory.get("policy", {}).get("comparison_window")
        if isinstance(candidate, int) and not isinstance(candidate, bool) and candidate > 0:
            memory_window = candidate
    window = memory_window or policy["variety_window"]
    entries = _memory_entries(series_memory, window)
    module_tokens = {
        module["id"]: {
            normalize_token(module["id"]),
            *{normalize_token(value) for value in module["variety_keys"]},
            *({normalize_token(module["archetype_id"])} if module["archetype_id"] else set()),
            *{normalize_token(value) for value in module["family_ids"]},
        }
        for module in modules
    }
    counts = {module["id"]: 0 for module in modules}
    matched_entries: list[dict[str, Any]] = []
    for index, entry in enumerate(entries, start=1):
        tokens = _walk_strings(entry)
        matched: set[str] = set()
        for module in modules:
            overlap = tokens & module_tokens[module["id"]]
            if overlap:
                counts[module["id"]] += 1
                matched.update(overlap)
        if matched:
            video_id = entry.get("video_id") or entry.get("id") or f"history-{index}"
            matched_entries.append(
                {"video_id": str(video_id), "matched_tokens": sorted(matched)}
            )

    total_occurrences = sum(counts.values())
    maximum_occurrences = max(counts.values(), default=0)
    penalty = min(
        policy["maximum_fatigue_penalty"],
        total_occurrences * policy["fatigue_penalty_per_occurrence"],
    )
    if not entries:
        signal = "no_history"
    elif maximum_occurrences >= policy["fatigue_warning_occurrences"]:
        signal = "warning"
    elif maximum_occurrences >= policy["fatigue_notice_occurrences"]:
        signal = "notice"
    else:
        signal = "clear"
    return {
        "window": window,
        "signal": signal,
        "penalty": round(penalty, 6),
        "matched_prior_entries": matched_entries,
        "is_quality_score": False,
    }


def _canonical_asset_type(value: Any) -> str | None:
    token = normalize_token(value)
    if not token:
        return None
    token = ASSET_TYPE_ALIASES.get(token, token)
    accepted = {
        "image",
        "icon",
        "video",
        "sfx",
        "music",
        "diagram",
        "cutout",
        "caption",
        "typographic_overlay",
        "logo",
    }
    return token if token in accepted else None


def _asset_types_from_index(asset_index: dict[str, Any] | None) -> set[str]:
    if asset_index is None:
        return set()
    found: set[str] = set()

    for asset in asset_index["assets"]:
        status = normalize_token(asset.get("status", ""))
        if status in BAD_ASSET_STATUSES:
            continue
        if asset.get("reuse", {}).get("policy") == "do_not_reuse":
            continue
        candidate = _canonical_asset_type(asset.get("type"))
        if candidate:
            found.add(candidate)
        semantic_tags = _normalized(asset.get("semantic_tags", []))
        intent_tags = _normalized(asset.get("intent_phrases", []))
        descriptive_tags = semantic_tags | intent_tags
        if descriptive_tags.intersection({"diagram", "diagrama", "chart", "infographic", "infografia"}):
            found.add("diagram")
        if descriptive_tags.intersection({"cutout", "alpha", "transparent", "transparente", "subject_mask"}):
            found.add("cutout")
        if descriptive_tags.intersection({"caption", "captions", "subtitle", "subtitulo", "subtitulos"}):
            found.add("caption")
        if descriptive_tags.intersection({"typography", "tipografia", "lettering", "text_overlay"}):
            found.add("typographic_overlay")
        asset_id = asset.get("asset_id")
        if isinstance(asset_id, str):
            prefix = normalize_token(asset_id).split("_", 1)[0]
            inferred = {
                "img": "image",
                "image": "image",
                "icon": "icon",
                "vis": "diagram",
                "sfx": "sfx",
                "bgm": "music",
                "music": "music",
                "logo": "logo",
            }.get(prefix)
            if inferred:
                found.add(inferred)
    return found


def _asset_report(
    modules: tuple[dict[str, Any], ...],
    asset_index: dict[str, Any] | None,
) -> tuple[dict[str, Any], float, list[str]]:
    required = sorted({value for module in modules for value in module["required_asset_types"]})
    preferred = sorted({value for module in modules for value in module["preferred_asset_types"]})
    available = sorted(_asset_types_from_index(asset_index))
    if asset_index is None:
        report = {
            "index_provided": False,
            "coverage_status": "unknown",
            "required_types": required,
            "available_types": [],
            "missing_types": [],
            "preferred_types_available": [],
        }
        warnings = ["asset_index_not_provided; resource coverage remains unverified"]
        return report, 0.0, warnings

    missing = sorted(set(required) - set(available))
    preferred_available = sorted(set(preferred) & set(available))
    report = {
        "index_provided": True,
        "coverage_status": "gaps" if missing else "covered",
        "required_types": required,
        "available_types": available,
        "missing_types": missing,
        "preferred_types_available": preferred_available,
    }
    penalty = min(0.12, len(missing) * 0.03)
    warnings = [f"missing_asset_types:{','.join(missing)}"] if missing else []
    return report, penalty, warnings


def _traceability_score(blueprint: dict[str, Any]) -> float:
    traceability = blueprint.get("traceability", {})
    sources = traceability.get("sources", [])
    decisions = traceability.get("decisions", [])
    unresolved = traceability.get("unresolved", [])
    base = 0.55
    if sources:
        base += 0.2
    if decisions:
        base += 0.2
    if unresolved:
        base -= min(0.15, len(unresolved) * 0.03)
    return max(0.0, min(1.0, base))


def _effort_report(
    modules: tuple[dict[str, Any], ...],
    asset_report: dict[str, Any],
) -> dict[str, Any]:
    missing_count = len(asset_report["missing_types"])
    points = sum(module["effort"]["points"] for module in modules) + missing_count * 2
    minutes_min = sum(module["effort"]["minutes_min"] for module in modules) + missing_count * 4
    minutes_max = sum(module["effort"]["minutes_max"] for module in modules) + missing_count * 12
    if points <= 15:
        level = "low"
    elif points <= 25:
        level = "medium"
    else:
        level = "high"
    return {
        "points": points,
        "level": level,
        "minutes_min": minutes_min,
        "minutes_max": minutes_max,
        "asset_generation_count": missing_count,
    }


def _confidence(
    fit_score: float,
    context: dict[str, Any],
    blueprint: dict[str, Any],
    asset_report: dict[str, Any],
) -> dict[str, Any]:
    completeness = context["categories_present"] / 5
    traceability = _traceability_score(blueprint)
    if asset_report["coverage_status"] == "covered":
        asset_certainty = 1.0
    elif asset_report["coverage_status"] == "gaps":
        asset_certainty = 0.65
    else:
        asset_certainty = 0.55
    score = max(
        0.0,
        min(1.0, fit_score * 0.68 + completeness * 0.17 + traceability * 0.1 + asset_certainty * 0.05),
    )
    if score >= 0.78:
        level = "high"
    elif score >= 0.58:
        level = "medium"
    else:
        level = "low"
    basis = [
        f"context_categories:{context['categories_present']}/5",
        f"traceability:{traceability:.3f}",
        f"asset_coverage:{asset_report['coverage_status']}",
    ]
    return {"score": round(score, 6), "level": level, "basis": basis}


def _face_safe_notes(blueprint: dict[str, Any], modules: tuple[dict[str, Any], ...]) -> list[str]:
    policy = blueprint["face_safe_policy"]
    protected = ", ".join(policy["protect"])
    placements = ", ".join(policy["preferred_placement_order"])
    notes = [
        f"Proteger {protected}; priorizar {placements}.",
        f"Cualquier cruce permitido dura como máximo {policy['max_face_crossing_s']:g}s y requiere revisión manual.",
    ]
    for module in modules:
        notes.extend(module["design_contract"]["notes"])
    return _unique(notes)


def _module_direction(module: dict[str, Any]) -> dict[str, Any]:
    return {
        "module_id": module["id"],
        "label": module["label"],
        "directives": module["directives"],
    }


def _family_attribution(
    modules: tuple[dict[str, Any], ...],
    kind_weights: dict[str, float],
) -> dict[str, Any]:
    """Attribute a hybrid recipe once while preserving every contribution."""
    weighted: dict[str, float] = defaultdict(float)
    module_counts: dict[str, int] = defaultdict(int)
    for module in modules:
        for family_id in module["family_ids"]:
            weighted[family_id] += float(kind_weights[module["kind"]])
            module_counts[family_id] += 1
    contributing = sorted(weighted)
    if not contributing:
        primary = None
    else:
        primary = sorted(
            contributing,
            key=lambda family_id: (
                -weighted[family_id],
                -module_counts[family_id],
                family_id,
            ),
        )[0]
    return {
        "primary_family_id": primary,
        "hybrid": len(contributing) > 1,
        "contributing_family_ids": contributing,
    }


def _candidate(
    scored_modules: tuple[dict[str, Any], ...],
    *,
    blueprint: dict[str, Any],
    context: dict[str, Any],
    catalog: dict[str, Any],
    series_contract: dict[str, Any] | None,
    series_memory: dict[str, Any] | None,
    asset_index: dict[str, Any] | None,
) -> dict[str, Any]:
    modules = tuple(item["module"] for item in scored_modules)
    weights = catalog["kind_weights"]
    base_fit = sum(
        weights[item["module"]["kind"]] * item["fit_score"] for item in scored_modules
    )
    fatigue = _fatigue_report(modules, series_memory, catalog["policy"])
    asset_report, asset_penalty, asset_warnings = _asset_report(modules, asset_index)
    fit_score = max(0.0, min(1.0, base_fit - fatigue["penalty"] - asset_penalty))
    confidence = _confidence(fit_score, context, blueprint, asset_report)
    warnings = list(asset_warnings)
    if fatigue["signal"] in {"notice", "warning"}:
        warnings.append(f"creative_fatigue:{fatigue['signal']}")
    if series_memory is None:
        warnings.append("series_memory_not_provided; fatigue cannot be evaluated")

    family_attribution = _family_attribution(modules, catalog["kind_weights"])
    candidate_families = family_attribution["contributing_family_ids"]
    if series_contract is not None:
        declared_families = {
            family["family_id"] for family in series_contract.get("template_families", [])
        }
        undeclared = sorted(set(candidate_families) - declared_families)
        if undeclared:
            warnings.append(
                f"catalog_families_not_declared_in_series_contract:{','.join(undeclared)}"
            )
        if not candidate_families:
            warnings.append("exploratory_recipe_without_declared_series_family")

    module_ids = {module["kind"]: module["id"] for module in modules}
    structure = next(module for module in modules if module["kind"] == "structure")
    visual = next(module for module in modules if module["kind"] == "visual_system")
    material = {
        "blueprint_id": blueprint["blueprint_id"],
        "module_ids": module_ids,
        "generator_version": GENERATOR_VERSION,
    }
    digest = hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()[:12].upper()
    blueprint_suffix = re.sub(r"[^A-Z0-9_-]+", "-", blueprint["blueprint_id"].upper()).strip("-")
    recipe_id = f"RECIPE-{blueprint_suffix}-{digest}"
    score_breakdown = [
        {
            "module_id": item["module"]["id"],
            "kind": item["module"]["kind"],
            "fit_score": item["fit_score"],
            "positive_matches": item["positive_matches"],
            "negative_matches": item["negative_matches"],
        }
        for item in scored_modules
    ]
    return {
        "recipe_id": recipe_id,
        "label": f"{structure['label']} · {visual['label']}",
        "module_ids": module_ids,
        **family_attribution,
        "fit_score": round(fit_score, 6),
        "confidence": confidence,
        "score_breakdown": score_breakdown,
        "compatibility": {
            "passed": True,
            "blocking_conflicts": [],
            "warnings": _unique(warnings),
        },
        "fatigue": fatigue,
        "asset_fit": asset_report,
        "effort": _effort_report(modules, asset_report),
        "creative_direction": {
            **{module["kind"]: _module_direction(module) for module in modules},
            "face_safe_notes": _face_safe_notes(blueprint, modules),
            "rhythm_pattern": blueprint["emotion_arc"]["rhythm_pattern"],
        },
        "explanation": (
            f"Combina {module_ids['hook']} con {module_ids['structure']} y {module_ids['visual_system']}; "
            f"ajuste contextual {fit_score:.3f}, confianza {confidence['score']:.3f}. "
            "La posición es un orden de revisión contextual, no una declaración de calidad ni un ganador universal."
        ),
    }


def _module_difference(left: dict[str, Any], right: dict[str, Any]) -> tuple[int, list[str]]:
    axes = [kind for kind in KINDS if left["module_ids"][kind] != right["module_ids"][kind]]
    return len(axes), axes


def _select_varied(
    candidates: list[dict[str, Any]],
    *,
    count: int,
    minimum_difference: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for candidate in candidates:
        if len(selected) >= count:
            break
        if selected:
            differences = [_module_difference(candidate, previous) for previous in selected]
            if any(amount < minimum_difference for amount, _ in differences):
                continue
            if any(
                not set(axes).intersection({"structure", "visual_system", "motion"})
                for _, axes in differences
            ):
                continue
        selected.append(candidate)
    return selected


def _reference(
    document: dict[str, Any] | None,
    path: str | None,
    digest: str | None,
) -> dict[str, Any]:
    if document is None:
        return {"path": None, "sha256": None}
    return {
        "path": path or "<in-memory>",
        "sha256": digest or canonical_sha256(document),
    }


def build_plan(
    blueprint: dict[str, Any],
    catalog: dict[str, Any],
    *,
    blueprint_path: str = "<in-memory-blueprint>",
    catalog_path: str = "<in-memory-catalog>",
    blueprint_sha256: str | None = None,
    catalog_sha256: str | None = None,
    series_contract: dict[str, Any] | None = None,
    series_contract_path: str | None = None,
    series_contract_sha256: str | None = None,
    series_memory: dict[str, Any] | None = None,
    series_memory_path: str | None = None,
    series_memory_sha256: str | None = None,
    asset_index: dict[str, Any] | None = None,
    asset_index_path: str | None = None,
    asset_index_sha256: str | None = None,
    count: int = 3,
    plan_id: str | None = None,
) -> dict[str, Any]:
    if isinstance(count, bool) or not isinstance(count, int) or count < 1 or count > 3:
        raise CreativeRecipeError("count must be an integer between 1 and 3")
    validate_blueprint(blueprint)
    validate_catalog(catalog)
    _validate_optional_inputs(series_contract, series_memory, asset_index)

    context = _context_from_blueprint(blueprint)
    policy = catalog["policy"]
    if plan_id is None:
        suffix = re.sub(r"[^A-Z0-9_-]+", "-", blueprint["blueprint_id"].upper()).strip("-")
        plan_id = f"RECIPE-PLAN-{suffix}"
    if not re.fullmatch(r"RECIPE-PLAN-[A-Z0-9_-]+", plan_id):
        raise CreativeRecipeError(f"Invalid plan id: {plan_id!r}")

    base = {
        "schema_version": "1.0.0",
        "plan_id": plan_id,
        "generator_version": GENERATOR_VERSION,
        "blueprint": {
            "id": blueprint["blueprint_id"],
            "video_id": blueprint["video_id"],
            "path": blueprint_path,
            "sha256": blueprint_sha256 or canonical_sha256(blueprint),
            "duration_target_s": blueprint["duration_target_s"],
        },
        "inputs": {
            "catalog": {
                "path": catalog_path,
                "sha256": catalog_sha256 or canonical_sha256(catalog),
            },
            "series_contract": _reference(
                series_contract, series_contract_path, series_contract_sha256
            ),
            "series_memory": _reference(series_memory, series_memory_path, series_memory_sha256),
            "asset_index": _reference(asset_index, asset_index_path, asset_index_sha256),
        },
        "recommendation_policy": {
            "max_proposals": 3,
            "minimum_fit_score": policy["minimum_fit_score"],
            "minimum_confidence_score": policy["minimum_confidence_score"],
            "minimum_module_differences_between_options": policy[
                "minimum_module_differences_between_options"
            ],
            "single_global_winner": False,
            "automatic_promotion": False,
            "human_choice_required": True,
            "preserve_multiple_families": True,
            "ranking_meaning": "contextual_review_order_not_quality_or_universal_winner",
        },
    }
    warnings: list[str] = []
    if series_contract is None:
        warnings.append("series_contract_not_provided; family constraints use catalog defaults")
    if series_memory is None:
        warnings.append("series_memory_not_provided; fatigue cannot be evaluated")
    if asset_index is None:
        warnings.append("asset_index_not_provided; resource coverage remains unverified")

    abstention_reasons: list[str] = []
    candidates: list[dict[str, Any]] = []
    if context["signal_count"] < 2:
        abstention_reasons.append("insufficient_blueprint_signals")
    else:
        eligible_by_kind: dict[str, list[dict[str, Any]]] = {kind: [] for kind in KINDS}
        for module in catalog["modules"]:
            scored = _score_module(module, context)
            if scored is not None:
                eligible_by_kind[module["kind"]].append(scored)
        for kind in KINDS:
            eligible_by_kind[kind].sort(
                key=lambda item: (-item["fit_score"], item["module"]["id"])
            )
        if any(not eligible_by_kind[kind] for kind in KINDS):
            abstention_reasons.append("no_eligible_modules")
        else:
            compatible_count = 0
            for scored_tuple in itertools.product(*(eligible_by_kind[kind] for kind in KINDS)):
                modules = tuple(item["module"] for item in scored_tuple)
                if _combination_conflicts(modules):
                    continue
                compatible_count += 1
                candidates.append(
                    _candidate(
                        scored_tuple,
                        blueprint=blueprint,
                        context=context,
                        catalog=catalog,
                        series_contract=series_contract,
                        series_memory=series_memory,
                        asset_index=asset_index,
                    )
                )
            if compatible_count == 0:
                abstention_reasons.append("no_compatible_combinations")

    candidates.sort(
        key=lambda item: (
            -item["fit_score"],
            -item["confidence"]["score"],
            item["fatigue"]["penalty"],
            item["effort"]["points"],
            tuple(item["module_ids"][kind] for kind in KINDS),
        )
    )
    fit_candidates = [
        candidate for candidate in candidates if candidate["fit_score"] >= policy["minimum_fit_score"]
    ]
    if candidates and not fit_candidates and not abstention_reasons:
        abstention_reasons.append("below_fit_threshold")
    confidence_candidates = [
        candidate
        for candidate in fit_candidates
        if candidate["confidence"]["score"] >= policy["minimum_confidence_score"]
    ]
    if fit_candidates and not confidence_candidates and not abstention_reasons:
        abstention_reasons.append("below_confidence_threshold")

    selected = _select_varied(
        confidence_candidates,
        count=min(count, policy["max_proposals"]),
        minimum_difference=policy["minimum_module_differences_between_options"],
    )
    if selected:
        first = selected[0]
        proposals = []
        for index, candidate in enumerate(selected):
            difference, axes = _module_difference(candidate, first)
            proposal = {
                "option_id": OPTION_IDS[index],
                **candidate,
                "rank": index + 1,
                "variety": {
                    "module_difference_from_first": difference,
                    "distinct_axes": axes,
                    "not_quality_score": True,
                },
            }
            proposals.append(proposal)
        plan = {
            **base,
            "status": "proposed",
            "abstention_reasons": [],
            "proposal_count": len(proposals),
            "proposals": proposals,
            "warnings": _unique(warnings),
            "explanation": (
                f"Se proponen {len(proposals)} recetas compatibles y deliberadamente distintas. "
                "El orden expresa ajuste al blueprint actual; la selección final requiere revisión humana "
                "y no promueve ninguna familia automáticamente."
            ),
        }
    else:
        if not abstention_reasons:
            abstention_reasons.append("no_compatible_combinations")
        plan = {
            **base,
            "status": "abstained",
            "abstention_reasons": _unique(abstention_reasons),
            "proposal_count": 0,
            "proposals": [],
            "warnings": _unique(warnings),
            "explanation": (
                "Abstención válida: los insumos no permiten proponer una combinación que supere "
                f"los umbrales y contratos declarados. Razones: {', '.join(_unique(abstention_reasons))}."
            ),
        }
    validate_plan(plan, catalog=catalog)
    return plan


def validate_plan(plan: dict[str, Any], *, catalog: dict[str, Any] | None = None) -> None:
    _validate_schema(plan, PLAN_SCHEMA, "Creative recipe plan")
    if plan["proposal_count"] != len(plan["proposals"]):
        raise CreativeRecipeError("proposal_count does not match proposals length")
    if plan["status"] == "proposed":
        if not plan["proposals"] or plan["abstention_reasons"]:
            raise CreativeRecipeError("A proposed plan needs proposals and no abstention reasons")
    else:
        if plan["proposals"] or plan["proposal_count"] != 0 or not plan["abstention_reasons"]:
            raise CreativeRecipeError("An abstained plan needs reasons and no proposals")
    if plan["recommendation_policy"]["single_global_winner"]:
        raise CreativeRecipeError("A creative recipe plan may not declare a global winner")
    if plan["recommendation_policy"]["automatic_promotion"]:
        raise CreativeRecipeError("A creative recipe plan may not promote recipes automatically")

    by_id = {module["id"]: module for module in catalog["modules"]} if catalog else {}
    expected_ranks = list(range(1, len(plan["proposals"]) + 1))
    if [proposal["rank"] for proposal in plan["proposals"]] != expected_ranks:
        raise CreativeRecipeError("Proposal ranks must be contiguous and start at 1")
    recipe_ids = [proposal["recipe_id"] for proposal in plan["proposals"]]
    if len(recipe_ids) != len(set(recipe_ids)):
        raise CreativeRecipeError("Recipe ids must be unique within a plan")
    for proposal in plan["proposals"]:
        if proposal["compatibility"]["blocking_conflicts"]:
            raise CreativeRecipeError("Proposed recipes may not contain blocking conflicts")
        contributing = proposal["contributing_family_ids"]
        primary = proposal["primary_family_id"]
        if contributing != sorted(set(contributing)):
            raise CreativeRecipeError("Contributing family ids must be sorted and unique")
        if proposal["hybrid"] is not (len(contributing) > 1):
            raise CreativeRecipeError("Hybrid flag does not match family contributions")
        if (primary is None) != (not contributing):
            raise CreativeRecipeError("Primary family must be null exactly when there are no contributors")
        if primary is not None and primary not in contributing:
            raise CreativeRecipeError("Primary family must be one of the contributing families")
        kinds = [item["kind"] for item in proposal["score_breakdown"]]
        if sorted(kinds) != sorted(KINDS):
            raise CreativeRecipeError("Each proposal must score every module kind exactly once")
        if catalog:
            unknown = sorted(set(proposal["module_ids"].values()) - set(by_id))
            if unknown:
                raise CreativeRecipeError(f"Proposal references unknown catalog modules: {unknown}")
            modules = tuple(by_id[module_id] for module_id in proposal["module_ids"].values())
            expected_attribution = _family_attribution(modules, catalog["kind_weights"])
            actual_attribution = {
                "primary_family_id": primary,
                "hybrid": proposal["hybrid"],
                "contributing_family_ids": contributing,
            }
            if actual_attribution != expected_attribution:
                raise CreativeRecipeError(
                    f"Proposal {proposal['recipe_id']} has inconsistent family attribution"
                )
            conflicts = _combination_conflicts(modules)
            if conflicts:
                raise CreativeRecipeError(
                    f"Proposal {proposal['recipe_id']} violates catalog compatibility: {conflicts}"
                )
            for kind, module_id in proposal["module_ids"].items():
                if by_id[module_id]["kind"] != kind:
                    raise CreativeRecipeError(
                        f"Proposal module {module_id} is not of declared kind {kind}"
                    )
    minimum_difference = plan["recommendation_policy"][
        "minimum_module_differences_between_options"
    ]
    for left, right in itertools.combinations(plan["proposals"], 2):
        difference, _ = _module_difference(left, right)
        if difference < minimum_difference:
            raise CreativeRecipeError("Proposed options are not different enough")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blueprint", required=True, help="Creative blueprint JSON")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Modular recipe catalog JSON")
    parser.add_argument("--series-contract", help="Optional series contract JSON")
    parser.add_argument("--series-memory", help="Optional variety ledger or usage memory JSON")
    parser.add_argument("--asset-index", help="Optional semantic asset index JSON")
    parser.add_argument("--count", type=int, default=3, help="Number of options, from 1 to 3")
    parser.add_argument("--plan-id", help="Explicit RECIPE-PLAN-* identifier")
    parser.add_argument("--out", help="Explicit output JSON path; stdout when omitted")
    parser.add_argument(
        "--require-proposals",
        action="store_true",
        help="Return exit code 1 when the valid result is an abstention",
    )
    args = parser.parse_args(argv)

    try:
        blueprint_path = _confined_path(args.blueprint, must_exist=True, expect="file")
        catalog_path = _confined_path(args.catalog, must_exist=True, expect="file")
        optional_paths: dict[str, Path | None] = {}
        for name, raw in (
            ("series_contract", args.series_contract),
            ("series_memory", args.series_memory),
            ("asset_index", args.asset_index),
        ):
            optional_paths[name] = (
                _confined_path(raw, must_exist=True, expect="file") if raw else None
            )
        blueprint = load_json(blueprint_path)
        catalog = load_json(catalog_path)
        series_contract = load_json(optional_paths["series_contract"]) if optional_paths["series_contract"] else None
        series_memory = load_json(optional_paths["series_memory"]) if optional_paths["series_memory"] else None
        asset_index = load_json(optional_paths["asset_index"]) if optional_paths["asset_index"] else None

        plan = build_plan(
            blueprint,
            catalog,
            blueprint_path=_portable_path(blueprint_path),
            catalog_path=_portable_path(catalog_path),
            blueprint_sha256=file_sha256(blueprint_path),
            catalog_sha256=file_sha256(catalog_path),
            series_contract=series_contract,
            series_contract_path=_portable_path(optional_paths["series_contract"]) if optional_paths["series_contract"] else None,
            series_contract_sha256=file_sha256(optional_paths["series_contract"]) if optional_paths["series_contract"] else None,
            series_memory=series_memory,
            series_memory_path=_portable_path(optional_paths["series_memory"]) if optional_paths["series_memory"] else None,
            series_memory_sha256=file_sha256(optional_paths["series_memory"]) if optional_paths["series_memory"] else None,
            asset_index=asset_index,
            asset_index_path=_portable_path(optional_paths["asset_index"]) if optional_paths["asset_index"] else None,
            asset_index_sha256=file_sha256(optional_paths["asset_index"]) if optional_paths["asset_index"] else None,
            count=args.count,
            plan_id=args.plan_id,
        )
        payload = json.dumps(plan, ensure_ascii=False, indent=2) + "\n"
        if args.out:
            protected = tuple(
                path
                for path in (blueprint_path, catalog_path, *optional_paths.values())
                if path is not None
            )
            _write_json(args.out, plan, protected_paths=protected)
        else:
            print(payload, end="")
        if args.require_proposals and plan["status"] != "proposed":
            return 1
        return 0
    except (CreativeRecipeError, OSError, KeyError, TypeError) as error:
        print(f"creative recipe error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
