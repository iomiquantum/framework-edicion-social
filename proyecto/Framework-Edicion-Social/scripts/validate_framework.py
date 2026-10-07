#!/usr/bin/env python3
"""Validate the reusable framework, its governed data, styles, and QA contract."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path, PurePosixPath, PureWindowsPath

import approval_receipt as approval_receipts
import compose_recipe
import performance_cohorts
import plan_platform_derivatives as platform_derivatives
from check_qa_scorecard import analyze_scorecard, is_initial_template
from schema_validation import UnsupportedSchemaKeyword, assert_supported_schema, validate_document


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
LIBRARY = ROOT / "library"
STYLE_CATALOG = ROOT / "styles/catalog.json"
FRAMEWORK_VERSION = "1.6.3"
QA_SCHEMA_CANONICAL_SHA256 = "636e64ce762865a9326bfaeb01f5b4580b6126bf8ceed8ec136cd91b4d94814b"
QA_SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"
QA_SCHEMA_ID = "https://local.framework-edicion-social/schemas/qa-scorecard.schema.json"

SIMPLE_TEMPLATE_SCHEMAS = {
    "creative-recipes/catalog.json": "schemas/creative-recipe-catalog.schema.json",
    "template-bank/registry.json": "schemas/template-bank-registry.schema.json",
    "templates/approval-receipt.json": "schemas/approval-receipt.schema.json",
    "templates/asset-index.json": "schemas/asset-index.schema.json",
    "templates/asset-lock.json": "schemas/asset-lock.schema.json",
    "templates/asset-usage-history.json": "schemas/asset-usage-history.schema.json",
    "templates/content-lock-evidence.json": "schemas/content-lock-evidence.schema.json",
    "templates/creative-attribution.json": "schemas/creative-attribution.schema.json",
    "templates/creative-blueprint.json": "schemas/creative-blueprint.schema.json",
    "templates/creative-recipe-plan.json": "schemas/creative-recipe-plan.schema.json",
    "templates/cut-plan.json": "schemas/cut-plan.schema.json",
    "templates/dependency-map.json": "schemas/dependency-map.schema.json",
    "templates/golden-master-registry.json": "schemas/golden-master-registry.schema.json",
    "templates/performance-cohort-report.json": "schemas/performance-cohort-report.schema.json",
    "templates/performance-observation.json": "schemas/performance-observation.schema.json",
    "templates/performance-review.json": "schemas/performance-review.schema.json",
    "templates/performance-store.json": "schemas/performance-store.schema.json",
    "templates/platform-adaptation.json": "schemas/platform-adaptation.schema.json",
    "templates/platform-master.json": "schemas/platform-master.schema.json",
    "templates/production-board.json": "schemas/production-board.schema.json",
    "templates/production-metrics.json": "schemas/production-metrics.schema.json",
    "templates/publication-registry.json": "schemas/publication-registry.schema.json",
    "templates/publish-package.json": "schemas/publish-package.schema.json",
    "templates/recording-preflight.json": "schemas/recording-preflight.schema.json",
    "templates/review-decision.json": "schemas/review-decision.schema.json",
    "templates/review-packet.json": "schemas/review-packet.schema.json",
    "templates/series-contract.json": "schemas/series-contract.schema.json",
    "templates/series-variety-ledger.json": "schemas/series-variety-ledger.schema.json",
    "templates/style-decision.json": "schemas/style-decision.schema.json",
    "templates/take-map.json": "schemas/take-map.schema.json",
    "templates/variant-plan.json": "schemas/variant-plan.schema.json",
    "templates/video-state.json": "schemas/video-state.schema.json",
    "learning/promotion-policy.v1.json": "schemas/learning-promotion-policy.schema.json",
    "master-profiles/editorial-mezzanine-hdr-001.json": "schemas/master-profile.schema.json",
    "master-profiles/social-delivery-sdr-001.json": "schemas/master-profile.schema.json",
}

SIMPLE_SCHEMA_PATHS = {
    "schemas/approval-receipt.schema.json",
    "schemas/asset-index.schema.json",
    "schemas/asset-lock.schema.json",
    "schemas/asset-usage-history.schema.json",
    "schemas/asset.schema.json",
    "schemas/content-lock-evidence.schema.json",
    "schemas/creative-attribution.schema.json",
    "schemas/creative-blueprint.schema.json",
    "schemas/creative-recipe-catalog.schema.json",
    "schemas/creative-recipe-plan.schema.json",
    "schemas/cut-plan.schema.json",
    "schemas/dependency-map.schema.json",
    "schemas/feedback-event.schema.json",
    "schemas/golden-master-registry.schema.json",
    "schemas/learning-evidence-event.schema.json",
    "schemas/learning-promotion-policy.schema.json",
    "schemas/learning-recommendation-report.schema.json",
    "schemas/master-profile.schema.json",
    "schemas/motion-style.schema.json",
    "schemas/performance-cohort-report.schema.json",
    "schemas/performance-observation.schema.json",
    "schemas/performance-review.schema.json",
    "schemas/performance-store.schema.json",
    "schemas/platform-adaptation.schema.json",
    "schemas/platform-master.schema.json",
    "schemas/platform-profile.schema.json",
    "schemas/production-board.schema.json",
    "schemas/production-metrics.schema.json",
    "schemas/publication-registry.schema.json",
    "schemas/publish-package.schema.json",
    "schemas/recording-preflight.schema.json",
    "schemas/review-decision.schema.json",
    "schemas/review-packet.schema.json",
    "schemas/rule.schema.json",
    "schemas/series-contract.schema.json",
    "schemas/series-fingerprint.schema.json",
    "schemas/series-variety-ledger.schema.json",
    "schemas/style-decision.schema.json",
    "schemas/style.schema.json",
    "schemas/take-map.schema.json",
    "schemas/template-bank-registry.schema.json",
    "schemas/variant-plan.schema.json",
    "schemas/video-state.schema.json",
}

ADVANCED_SCHEMA_PATHS = {"schemas/qa-scorecard.schema.json"}


def load(relative):
    path = ROOT / relative
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_sha256(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def validate_qa_schema_contract(schema):
    """Pin the advanced schema without routing it through the subset validator."""
    if not isinstance(schema, dict):
        raise ValueError("QA scorecard schema must be an object")
    if schema.get("$schema") != QA_SCHEMA_DRAFT or schema.get("$id") != QA_SCHEMA_ID:
        raise ValueError("QA scorecard schema draft or id drift")
    actual_hash = canonical_json_sha256(schema)
    if actual_hash != QA_SCHEMA_CANONICAL_SHA256:
        raise ValueError(
            "QA scorecard schema contract drift: "
            f"expected {QA_SCHEMA_CANONICAL_SHA256}, got {actual_hash}; "
            "review advanced semantics and update the pinned hash intentionally"
        )


def require_schema_match(label, value, schema, path="$"):
    errors = validate_document(value, schema, path)
    if errors:
        details = "\n  - ".join(errors)
        raise ValueError(f"{label} does not match its schema:\n  - {details}")


def validate_assets(catalog, asset_schema):
    seen = set()
    pattern = re.compile(r"^[A-Z]{3,4}-[A-Z0-9]+-[0-9]{4}$")
    assets = catalog.get("assets")
    if not isinstance(assets, list):
        raise ValueError("library/catalog.json must contain an assets array")
    for index, asset in enumerate(assets):
        require_schema_match("library asset", asset, asset_schema, f"$.assets[{index}]")
        asset_id = asset["id"]
        if asset_id in seen:
            raise ValueError(f"Duplicate asset id: {asset_id}")
        if not pattern.fullmatch(asset_id):
            raise ValueError(f"Invalid asset id: {asset_id}")
        seen.add(asset_id)
        path = (LIBRARY / asset["file"]).resolve()
        try:
            path.relative_to(LIBRARY.resolve())
        except ValueError as error:
            raise ValueError(f"Asset escapes library: {asset_id}") from error
        if not path.is_file():
            raise FileNotFoundError(f"Missing asset: {asset_id} -> {path}")
        if sha256(path) != asset["sha256"]:
            raise ValueError(f"Hash mismatch: {asset_id}")
        reuse = asset["reuse"]
        if reuse["usage_count"] < len(reuse["used_in"]):
            raise ValueError(f"Usage count lower than project list: {asset_id}")
        if asset.get("status") == "deprecated":
            approval = asset.get("approval", {})
            if approval.get("reuse_status") not in {None, "ineligible"}:
                raise ValueError(f"Deprecated asset remains reusable: {asset_id}")
    return len(seen)


def validate_preferences(preferences):
    ids = set()
    for key in ("confirmed_preferences", "candidate_preferences", "scoped_rejections"):
        items = preferences.get(key)
        if not isinstance(items, list):
            raise ValueError(f"Preference profile is missing array {key}")
        for item in items:
            item_id = item["id"]
            if item_id in ids:
                raise ValueError(f"Duplicate preference id: {item_id}")
            ids.add(item_id)
    return len(ids)


def validate_feedback(feedback_schema):
    path = ROOT / "feedback/events.jsonl"
    seen = set()
    count = 0
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid feedback JSON at line {line_number}: {error}") from error
            require_schema_match("feedback event", event, feedback_schema, f"$line[{line_number}]")
            event_id = event["event_id"]
            if event_id in seen:
                raise ValueError(f"Duplicate feedback event: {event_id}")
            seen.add(event_id)
            date.fromisoformat(event["recorded_at"])
            if not event["explicit_user_feedback"] and event["preference_effect"] in {"candidate", "confirmed_global"}:
                raise ValueError(f"Inferred feedback cannot promote preference: {event_id}")
            count += 1
    return count


def validate_rules(registry, rule_schema):
    rules = registry.get("rules")
    if not isinstance(rules, list):
        raise ValueError("rules/registry.json must contain a rules array")
    seen = set()
    for index, rule in enumerate(rules):
        require_schema_match("editorial rule", rule, rule_schema, f"$.rules[{index}]")
        key = (rule["id"], rule["version"])
        if key in seen:
            raise ValueError(f"Duplicate rule: {key}")
        seen.add(key)
        date.fromisoformat(rule["review_due_at"])
        if rule["status"] == "adopted" and rule["kind"] in {"editorial_hypothesis", "trend"} and not rule.get("approval"):
            raise ValueError(f"Unapproved adopted creative rule: {rule['id']}")
    return len(rules)


def style_package_sha256(root):
    """Hash every regular package file using its normalized relative path."""
    digest = hashlib.sha256()
    root = Path(root)
    files = []
    for entry in root.rglob("*"):
        relative = entry.relative_to(root).as_posix()
        if entry.is_symlink():
            raise ValueError(f"Style package may not contain symlinks: {relative}")
        if entry.is_dir():
            continue
        if not entry.is_file():
            raise ValueError(f"Unsupported style package entry: {relative}")
        files.append((relative, entry))
    for relative, path in sorted(files):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


def path_without_symlinks(base, parts, label):
    """Build a lexical relative path while rejecting every symlink component."""
    cursor = Path(base)
    if cursor.is_symlink():
        raise ValueError(f"{label} may not traverse symlinks: {cursor}")
    for part in parts:
        cursor = cursor.parent if part == ".." else cursor / part
        if cursor.is_symlink():
            raise ValueError(f"{label} may not traverse symlinks: {cursor}")
    return cursor


def portable_style_root(style_id, raw):
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"Missing canonical_path for {style_id}")
    if "\\" in raw or PurePosixPath(raw).is_absolute() or PureWindowsPath(raw).is_absolute():
        raise ValueError(f"Non-portable canonical_path for {style_id}: {raw}")
    pure = PurePosixPath(raw)
    if raw != pure.as_posix() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"canonical_path must be normalized and traversal-free for {style_id}: {raw}")
    if pure.parts != ("styles", style_id):
        raise ValueError(f"canonical_path must be styles/{style_id}, got {raw}")
    candidate = path_without_symlinks(ROOT, pure.parts, f"Style package {style_id}")
    resolved = candidate.resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as error:
        raise ValueError(f"Style escapes framework root: {style_id}") from error
    if not resolved.is_dir():
        raise FileNotFoundError(f"Missing style package: {style_id} -> {resolved}")
    return resolved


def portable_style_reference(style_id, field, raw):
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"Style {style_id} has invalid {field}")
    if "\\" in raw or PurePosixPath(raw).is_absolute() or PureWindowsPath(raw).is_absolute():
        raise ValueError(f"Style {style_id} has non-portable absolute {field}: {raw}")
    pure = PurePosixPath(raw)
    if raw != pure.as_posix() or any(part in {"", "."} for part in pure.parts):
        raise ValueError(f"Style {style_id} has non-normalized {field}: {raw}")
    candidate = path_without_symlinks(
        STYLE_CATALOG.parent,
        pure.parts,
        f"Style {style_id} {field}",
    )
    resolved = candidate.resolve()
    try:
        resolved.relative_to(WORKSPACE_ROOT.resolve())
    except ValueError as error:
        raise ValueError(f"Style {style_id} {field} escapes the shared workspace: {raw}") from error
    if not resolved.is_file():
        raise FileNotFoundError(f"Style {style_id} {field} does not exist: {raw}")
    return resolved


def validate_styles(catalog, style_schema, motion_schema):
    if not isinstance(catalog, dict):
        raise ValueError("styles/catalog.json must be an object")
    styles = catalog.get("styles")
    if not isinstance(styles, list) or not styles:
        raise ValueError("styles/catalog.json must contain at least one style")
    seen = set()
    for style in styles:
        if not isinstance(style, dict):
            raise ValueError("Each style catalog entry must be an object")
        style_id = style.get("id")
        if not isinstance(style_id, str):
            raise ValueError("Style catalog entry is missing id")
        if style_id in seen:
            raise ValueError(f"Duplicate style id: {style_id}")
        seen.add(style_id)
        root = portable_style_root(style_id, style.get("canonical_path"))
        for field in ("validated_preview", "implementation"):
            portable_style_reference(style_id, field, style.get(field))
        for name in ("README.md", "motion.json", "style.json"):
            target = root / name
            if not target.is_file():
                raise FileNotFoundError(f"Style {style_id} is missing {name}")
            if target.is_symlink():
                raise ValueError(f"Style file may not be a symlink: {target}")
        style_data = json.loads((root / "style.json").read_text(encoding="utf-8"))
        motion_data = json.loads((root / "motion.json").read_text(encoding="utf-8"))
        require_schema_match(f"{style_id}/style.json", style_data, style_schema)
        require_schema_match(f"{style_id}/motion.json", motion_data, motion_schema)
        if style_data["id"] != style_id or motion_data["style_id"] != style_id:
            raise ValueError(f"Style identifier drift: {style_id}")
        if style_data["version"] != motion_data["version"] or style.get("version") != style_data["version"]:
            raise ValueError(f"Style version drift: {style_id}")
        if style.get("status") != style_data.get("status"):
            raise ValueError(f"Style status drift: {style_id}")
        declared_hash = style.get("package_sha256")
        if not isinstance(declared_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", declared_hash):
            raise ValueError(f"Style package hash is missing or invalid: {style_id}")
        actual_hash = style_package_sha256(root)
        if actual_hash != declared_hash:
            raise ValueError(f"Style package hash drift: {style_id}; expected {declared_hash}, got {actual_hash}")
    weights = catalog.get("selection_weights", {})
    if not isinstance(weights, dict) or not weights or any(
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or isinstance(value, float) and not math.isfinite(value)
        or value < 0
        or value > 1
        for value in weights.values()
    ):
        raise ValueError("Style selection weights must be finite numbers between 0 and 1")
    if abs(math.fsum(float(value) for value in weights.values()) - 1.0) > 1e-9:
        raise ValueError("Style selection weights must sum to 1.0")
    return len(seen)


def validate_platform_profiles(catalog, profile_schema, known_source_urls=None):
    """Validate the governed platform catalog and its cross-profile invariants."""
    if not isinstance(catalog, dict):
        raise ValueError("platforms/catalog.json must be an object")
    if catalog.get("schema_version") != "1.0.0":
        raise ValueError("Unsupported platform catalog schema_version")
    catalog_version = catalog.get("catalog_version")
    if not isinstance(catalog_version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", catalog_version):
        raise ValueError("Platform catalog_version must be semantic")
    date.fromisoformat(catalog.get("updated_at", ""))
    profiles = catalog.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("platforms/catalog.json must contain profiles")

    seen = set()
    master_ids = []
    derivative_ids = set()
    for index, profile in enumerate(profiles):
        require_schema_match("platform profile", profile, profile_schema, f"$.profiles[{index}]")
        profile_id = profile["id"]
        if profile_id in seen:
            raise ValueError(f"Duplicate platform profile id: {profile_id}")
        seen.add(profile_id)
        if profile["kind"] == "master":
            master_ids.append(profile_id)
        else:
            derivative_ids.add(profile_id)

        safe_zones = profile["internal_defaults"]["safe_zones"]
        for rect_name in ("action", "title", "essential", "captions"):
            rect = safe_zones[rect_name]
            if rect["width"] <= 0 or rect["height"] <= 0:
                raise ValueError(f"{profile_id} {rect_name} safe zone must have positive area")
            if rect["x"] + rect["width"] > 1 + 1e-9 or rect["y"] + rect["height"] > 1 + 1e-9:
                raise ValueError(f"{profile_id} {rect_name} safe zone escapes the normalized canvas")
        for exclusion in safe_zones["exclusions"]:
            if exclusion["width"] <= 0 or exclusion["height"] <= 0:
                raise ValueError(f"{profile_id} exclusion {exclusion['id']} must have positive area")
            if exclusion["x"] + exclusion["width"] > 1 + 1e-9 or exclusion["y"] + exclusion["height"] > 1 + 1e-9:
                raise ValueError(f"{profile_id} exclusion {exclusion['id']} escapes the normalized canvas")

        official = profile["official_constraints"]
        for claim in official["claims"]:
            if not claim["source_url"].startswith("https://"):
                raise ValueError(f"{profile_id} claim {claim['id']} lacks an HTTPS source")
            if known_source_urls is not None and claim["source_url"] not in known_source_urls:
                raise ValueError(f"{profile_id} claim {claim['id']} is missing from sources/catalog.json")
        for constraint in official["automated_constraints"]:
            if not constraint["source_url"].startswith("https://"):
                raise ValueError(f"{profile_id} constraint {constraint['id']} lacks an HTTPS source")
            if known_source_urls is not None and constraint["source_url"] not in known_source_urls:
                raise ValueError(f"{profile_id} constraint {constraint['id']} is missing from sources/catalog.json")

    if master_ids != ["PLATFORM-MASTER-VERTICAL-001"]:
        raise ValueError("Platform catalog must contain exactly the neutral vertical master")
    required_derivatives = {
        "PLATFORM-INSTAGRAM-REELS-ORGANIC-001",
        "PLATFORM-TIKTOK-ORGANIC-001",
        "PLATFORM-YOUTUBE-SHORTS-001",
    }
    missing = sorted(required_derivatives - derivative_ids)
    if missing:
        raise ValueError(f"Platform catalog is missing required derivatives: {', '.join(missing)}")
    return len(seen)


def validate_qa_template(scorecard):
    # Deliberately do not pass the advanced QA schema through schema_validation.py.
    if not is_initial_template(scorecard):
        raise ValueError("QA scorecard template is not in its untouched initial state")
    report = analyze_scorecard(scorecard, template_mode=True)
    if not report["valid"]:
        details = "\n  - ".join(
            f"{item['code']} {item['path']}: {item['message']}" for item in report["errors"]
        )
        raise ValueError(f"QA scorecard template is semantically invalid:\n  - {details}")
    if scorecard.get("summary", {}).get("delivery_allowed") is not False:
        raise ValueError("QA template must begin with delivery_allowed=false")
    return report["counts"]


def validate_learning_contracts(approval_template, policy, series_contract, master_profiles):
    """Protect the human-review and non-overfitting invariants of v1.5."""
    if approval_template["decision"]["status"] != "pending":
        raise ValueError("Approval template must begin pending")
    if approval_template["decision"]["explicit_user_approval"] is not False:
        raise ValueError("Approval template cannot infer user approval")
    if approval_template["artifact"]["binding_status"] != "unbound":
        raise ValueError("Approval template must begin unbound")

    governance = policy["governance"]
    required_policy = {
        "automatic_promotion": False,
        "registry_write_permitted": False,
        "human_review_required": True,
        "scope_escalation_allowed": False,
        "single_template_winner": False,
        "recommendations_non_binding": True,
    }
    if any(governance.get(key) is not value for key, value in required_policy.items()):
        raise ValueError("Learning policy may only recommend contextual patterns for human review")

    if series_contract["seed_policy"]["rule"] != "reference_not_law":
        raise ValueError("Series seed must remain a reference, not an automatic law")
    if series_contract["seed_policy"]["automatic_enforcement"] is not False:
        raise ValueError("Series seed cannot be enforced automatically")
    quality = series_contract["quality_policy"]
    if quality["similarity_is_quality_score"] is not False or quality["similarity_can_fail_quality"] is not False:
        raise ValueError("Similarity may not become a quality score or hard fail")
    if not quality["human_creative_review_required"] or not quality["technical_qa_required"]:
        raise ValueError("Series memory cannot bypass creative review or technical QA")
    family_policy = series_contract["family_policy"]
    if family_policy["single_global_winner"] or not family_policy["preserve_multiple_families"]:
        raise ValueError("Series contract must preserve a contextual template portfolio")
    if series_contract["promotion_policy"]["default_minimum_approved_videos"] < 2:
        raise ValueError("A series default needs at least two approved videos unless explicitly instructed")
    if series_contract["recalibration_policy"]["minimum_approved_videos"] < 3:
        raise ValueError("Series recalibration cannot begin before three approvals")

    by_role = {profile["artifact_role"]: profile for profile in master_profiles}
    if set(by_role) != {"editorial_mezzanine", "social_delivery_master"}:
        raise ValueError("Exactly one editorial mezzanine and one social delivery profile are required")
    editorial = by_role["editorial_mezzanine"]
    delivery = by_role["social_delivery_master"]
    if editorial["governance"]["upload_ready"]:
        raise ValueError("Editorial HDR mezzanine cannot claim upload readiness")
    if not delivery["governance"]["requires_approved_source_receipt"]:
        raise ValueError("Social delivery master must require an approved source receipt")
    if delivery["governance"]["required_source_media_role"] != "editorial_mezzanine":
        raise ValueError("Social delivery lineage must point to the editorial mezzanine")
    if not delivery["governance"]["source_hash_must_differ"]:
        raise ValueError("Social delivery must be a distinct derived artifact")

    return {
        "template_families": len(series_contract["template_families"]),
        "master_profiles": len(master_profiles),
    }


def template_bank_path(raw, label, *, expect):
    """Resolve one portable template-bank reference without following symlinks."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"{label} must be a non-empty workspace-relative path")
    normalized = raw.replace("\\", "/")
    portable = PurePosixPath(normalized)
    windows = PureWindowsPath(raw)
    if portable.is_absolute() or windows.is_absolute() or ".." in portable.parts:
        raise ValueError(f"{label} must stay inside the workspace: {raw}")
    path = path_without_symlinks(WORKSPACE_ROOT, portable.parts, label)
    try:
        path.resolve().relative_to(WORKSPACE_ROOT.resolve())
    except ValueError as error:
        raise ValueError(f"{label} escapes the workspace: {raw}") from error
    if expect == "file" and not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {raw}")
    if expect == "dir" and not path.is_dir():
        raise FileNotFoundError(f"Missing {label}: {raw}")
    return path


def validate_template_bank(registry, registry_schema, approval_schema):
    """Enforce independent artifact, reuse, maturity, and performance states."""
    require_schema_match("template-bank/registry.json", registry, registry_schema)
    date.fromisoformat(registry["updated_at"])
    seen = set()
    default_reuse_states = {"series_default", "creator_default"}

    for template in registry["templates"]:
        label = f"template-bank entry {template['id']}"
        template_id = template["id"]
        if template_id in seen:
            raise ValueError(f"Duplicate template id: {template_id}")
        seen.add(template_id)

        source_project = template["source_project"]
        maturity = template["status"]
        artifact = template["artifact_approval"]
        reuse = template["template_reuse"]
        performance = template["performance"]

        if maturity == "planned":
            if source_project is not None:
                raise ValueError(f"{label}: a planned family cannot claim a source project")
            if artifact["status"] != "not_applicable" or reuse["status"] != "not_applicable":
                raise ValueError(f"{label}: a planned family must keep artifact and reuse not_applicable")
        elif source_project is None:
            raise ValueError(f"{label}: {maturity} family requires a source project")
        elif maturity != "retired":
            template_bank_path(source_project, f"{label} source_project", expect="dir")

        artifact_status = artifact["status"]
        if artifact_status == "not_applicable":
            if any(artifact[key] is not None for key in ("video_id", "receipt_path", "scope")):
                raise ValueError(f"{label}: not_applicable artifact cannot carry video, receipt, or scope")
        elif artifact_status in {"pending_review", "pending_receipt"}:
            if artifact["video_id"] is None:
                raise ValueError(f"{label}: pending artifact state requires video_id")
            if artifact["receipt_path"] is not None or artifact["scope"] is not None:
                raise ValueError(f"{label}: pending artifact state cannot claim receipt or approved scope")
        else:
            if artifact["video_id"] is None or artifact["receipt_path"] is None:
                raise ValueError(f"{label}: decided artifact state requires video_id and receipt_path")
            receipt_path = template_bank_path(
                artifact["receipt_path"], f"{label} approval receipt", expect="file"
            )
            with receipt_path.open(encoding="utf-8") as handle:
                receipt = json.load(handle)
            require_schema_match(f"{label} approval receipt", receipt, approval_schema)
            receipt_report = approval_receipts.verify_receipt(
                receipt,
                receipt_path=receipt_path,
                schema_path=ROOT / "schemas/approval-receipt.schema.json",
            )
            if receipt_report["document_status"] != "valid":
                raise ValueError(
                    f"{label}: approval receipt failed integrity verification: "
                    + "; ".join(receipt_report["errors"])
                )
            if receipt_report["artifact_status"] != "match" or receipt_report["binding_status"] != "match":
                raise ValueError(f"{label}: approval receipt is not bound to its current artifact")
            decision = receipt["decision"]
            if receipt["video_id"] != artifact["video_id"]:
                raise ValueError(f"{label}: receipt belongs to a different video")
            if decision["status"] != artifact_status:
                raise ValueError(f"{label}: registry artifact status disagrees with its receipt")
            if receipt["artifact"]["binding_status"] != "bound":
                raise ValueError(f"{label}: decided artifact receipt must be hash-bound")
            if artifact_status == "approved":
                if not receipt_report["usable_as_approval"]:
                    raise ValueError(f"{label}: receipt is not a usable explicit approval")
                if decision["explicit_user_approval"] is not True:
                    raise ValueError(f"{label}: approved artifact requires explicit user approval")
                receipt_scope = decision["scope"]
                expected_scope = "whole_artifact" if receipt_scope["whole_artifact"] else "layer_specific"
                if artifact["scope"] != expected_scope:
                    raise ValueError(f"{label}: artifact scope disagrees with its receipt")
            elif artifact["scope"] is not None:
                raise ValueError(f"{label}: non-approved decision cannot claim approved scope")

        reuse_status = reuse["status"]
        if reuse_status in {"not_applicable", "pending"}:
            if (
                reuse["scope"] is not None
                or reuse["authorization_basis"] != "none"
                or reuse["authorization_ref"] is not None
                or reuse["evidence_video_ids"]
            ):
                raise ValueError(f"{label}: inactive template reuse cannot carry authorization evidence")
        elif reuse_status in default_reuse_states:
            expected_scope = "series" if reuse_status == "series_default" else "creator"
            if reuse["scope"] != expected_scope:
                raise ValueError(f"{label}: {reuse_status} requires {expected_scope} scope")
            if artifact_status != "approved":
                raise ValueError(f"{label}: template reuse requires an independently approved source artifact")
            if reuse["authorization_basis"] not in {"explicit_template_approval", "approved_pattern"}:
                raise ValueError(f"{label}: template reuse requires independent authorization basis")
            if reuse["authorization_ref"] is None:
                raise ValueError(f"{label}: template reuse requires its own authorization reference")
            if reuse["authorization_ref"] == artifact["receipt_path"]:
                raise ValueError(f"{label}: artifact receipt cannot authorize template reuse")
            if reuse["authorization_basis"] == "approved_pattern" and len(reuse["evidence_video_ids"]) < 2:
                raise ValueError(f"{label}: approved_pattern requires at least two distinct videos")
        else:
            if reuse["scope"] is not None:
                raise ValueError(f"{label}: retired reuse cannot retain an active scope")
            if reuse["authorization_basis"] != "manual_retirement" or reuse["authorization_ref"] is None:
                raise ValueError(f"{label}: retired reuse requires an explicit retirement reference")

        performance_status = performance["status"]
        if performance_status == "no_data":
            if performance["network_tests"] != 0 or performance["review_refs"]:
                raise ValueError(f"{label}: no_data performance cannot claim tests or reviews")
        elif performance_status in {"inconclusive", "context_supported", "context_opposed", "expired"}:
            if performance["network_tests"] < 1 or not performance["review_refs"]:
                raise ValueError(f"{label}: {performance_status} performance requires tests and review references")

    return len(seen)


def validate_asset_intelligence_contract(index, usage_history):
    """Protect exact deduplication, advisory fatigue, and unambiguous usage history."""
    capabilities = index["capabilities"]
    if capabilities["exact_content_deduplication"] is not True:
        raise ValueError("Asset index must preserve exact SHA-256 deduplication")
    if capabilities["semantic_metadata_ranking"] is not True:
        raise ValueError("Asset index must preserve declared-metadata semantic ranking")
    if capabilities["perceptual_visual_similarity"] is not False:
        raise ValueError("Asset index may not claim perceptual visual similarity")
    if index["fatigue_policy"]["mode"] != "advisory_non_blocking":
        raise ValueError("Asset fatigue must remain advisory and non-blocking")

    assets = index["assets"]
    groups = index["exact_duplicate_groups"]
    summary = index["summary"]
    if summary["asset_count"] != len(assets):
        raise ValueError("Asset index summary asset_count drift")
    if summary["exact_duplicate_group_count"] != len(groups):
        raise ValueError("Asset index summary duplicate count drift")

    by_id = {}
    by_hash = {}
    for asset in assets:
        asset_id = asset["asset_id"]
        digest = asset["sha256"]
        if asset_id in by_id:
            raise ValueError(f"Duplicate indexed asset id: {asset_id}")
        if digest in by_hash:
            raise ValueError(
                f"Exact duplicate hashes must merge into one canonical asset: {digest}"
            )
        by_id[asset_id] = asset
        by_hash[digest] = asset

    for group in groups:
        asset = by_id.get(group["canonical_asset_id"])
        if asset is None or asset["sha256"] != group["sha256"]:
            raise ValueError("Exact duplicate group does not resolve to its canonical asset/hash")
        if group.get("proof") != "exact_sha256":
            raise ValueError("Duplicate groups require exact_sha256 proof")
        if not set(group["locations"]).issubset(set(asset["locations"])):
            raise ValueError("Duplicate group locations must belong to the canonical asset")

    event_ids = set()
    for event in usage_history["events"]:
        event_id = event["event_id"]
        if event_id in event_ids:
            raise ValueError(f"Duplicate asset usage event: {event_id}")
        event_ids.add(event_id)
        locators = [name for name in ("asset_id", "sha256", "path") if event.get(name)]
        if len(locators) != 1:
            raise ValueError(
                f"Asset usage event {event_id} must contain exactly one locator"
            )
    return {"indexed_assets": len(assets), "usage_events": len(event_ids)}


def validate_recipe_contract(catalog, plan):
    """Keep recipes contextual, human-selected, diverse, and reproducible."""
    compose_recipe.validate_catalog(catalog)
    compose_recipe.validate_plan(plan, catalog=catalog)

    required_kinds = {"hook", "structure", "visual_system", "motion", "sound", "cta"}
    counts = {kind: 0 for kind in required_kinds}
    module_ids = set()
    for module in catalog["modules"]:
        module_id = module["id"]
        if module_id in module_ids:
            raise ValueError(f"Duplicate creative recipe module: {module_id}")
        module_ids.add(module_id)
        counts[module["kind"]] += 1
    if any(counts[kind] < 3 for kind in required_kinds):
        raise ValueError("Creative recipe catalog needs at least three modules for every axis")

    policy = plan["recommendation_policy"]
    if (
        policy["single_global_winner"] is not False
        or policy["automatic_promotion"] is not False
        or policy["human_choice_required"] is not True
        or policy["preserve_multiple_families"] is not True
    ):
        raise ValueError("Creative recipes must remain contextual proposals for human choice")

    references = {
        "blueprint": plan["blueprint"],
        "catalog": plan["inputs"]["catalog"],
    }
    for label, reference in references.items():
        path = template_bank_path(
            reference["path"], f"creative recipe template {label}", expect="file"
        )
        if sha256(path) != reference["sha256"]:
            raise ValueError(f"Creative recipe template {label} hash drift")
    return {"recipe_modules": len(module_ids), "recipe_proposals": len(plan["proposals"])}


def validate_review_and_publish_templates(review, content_lock, publish):
    """Ensure untouched coordination and delivery templates fail closed."""
    if review["requested_changes"]:
        raise ValueError("Review packet template must start without requested changes")
    if review["preview_plan"]["strategy"] != "no_changes":
        raise ValueError("Review packet template must not prescribe a preview before feedback")
    if not review["inputs"].get("dependency_map"):
        raise ValueError("Review packet must bind its dependency map")
    governance = review["governance"]
    if (
        governance["review_decision_replaces_approval_receipt"] is not False
        or governance["approval_authority"] != "approval_receipt_only"
    ):
        raise ValueError("Review coordination may not replace an approval receipt")
    for scope, decision in review["decisions"].items():
        if decision != {"status": "pending", "evidence_reference": None}:
            raise ValueError(f"Review packet template decision {scope} must begin pending")

    if content_lock["status"] != "pending" or content_lock["artifacts"]:
        raise ValueError("Content-lock evidence template must begin pending and empty")
    if content_lock["platform_master_sha256"] is not None:
        raise ValueError("Content-lock template may not claim an unverified platform master")
    if content_lock["binding"]["payload_sha256"] is not None:
        raise ValueError("Content-lock template may not begin sealed")

    if publish["status"] != "blocked" or not publish["blocking_reasons"]:
        raise ValueError("Publish package template must begin blocked")
    platform_derivatives.verify_document_binding(publish, "publish package template")
    publish_governance = publish["governance"]
    if (
        publish_governance["auto_publish"] is not False
        or publish_governance["reedit_master"] is not False
        or publish_governance["human_publication_approval_required"] is not True
        or publish_governance["cryptographic_identity_established"] is not False
    ):
        raise ValueError("Publish package governance must remain fail-closed and human-approved")
    for target in publish["targets"]:
        if target["status"] != "blocked":
            raise ValueError("Publish package template targets must begin blocked")
        if any(gate["status"] != "pending" for gate in target["gates"]):
            raise ValueError("Publish package template gates must begin pending")
        if set(target["required_gates"]) != {gate["id"] for gate in target["gates"]}:
            raise ValueError("Publish target required gates and gate records must match")
    return {"review_decisions": len(review["decisions"]), "publish_targets": len(publish["targets"])}


def validate_performance_templates(
    attribution, registry, observation, store, report, production
):
    """Keep performance evidence publication-bound, reproducible, and non-causal."""
    expected_attribution_id = performance_cohorts.creative_attribution_id(attribution)
    if attribution["attribution_id"] != expected_attribution_id:
        raise ValueError(
            "Creative attribution id is not reproducible: "
            f"expected {expected_attribution_id}"
        )
    attribution_plan = attribution["plan"]
    plan_path = template_bank_path(
        attribution_plan["path"], "creative attribution recipe plan", expect="file"
    )
    if sha256(plan_path) != attribution_plan["sha256"]:
        raise ValueError("Creative attribution recipe plan hash drift")
    with plan_path.open(encoding="utf-8") as handle:
        selected_plan = json.load(handle)
    if selected_plan.get("plan_id") != attribution_plan["plan_id"]:
        raise ValueError("Creative attribution plan_id drifts from its recipe plan")
    selection = attribution["selection"]
    matches = [
        proposal
        for proposal in selected_plan.get("proposals", [])
        if proposal.get("option_id") == selection["option_id"]
        and proposal.get("recipe_id") == selection["recipe_id"]
    ]
    if len(matches) != 1:
        raise ValueError("Creative attribution must select exactly one real proposal")
    proposal = matches[0]
    expected_selection = {
        "option_id": proposal["option_id"],
        "recipe_id": proposal["recipe_id"],
        "primary_family_id": proposal["primary_family_id"],
        "hybrid": proposal["hybrid"],
        "contributing_family_ids": proposal["contributing_family_ids"],
        "module_ids": proposal["module_ids"],
    }
    if selection != expected_selection:
        raise ValueError("Creative attribution selection drifts from its recipe proposal")

    records = registry["records"]
    record_ids = set()
    publication_ids = set()
    for record in records:
        if record["record_id"] in record_ids:
            raise ValueError(f"Duplicate publication record id: {record['record_id']}")
        if record["publication_id"] in publication_ids:
            raise ValueError(f"Duplicate publication id: {record['publication_id']}")
        record_ids.add(record["record_id"])
        publication_ids.add(record["publication_id"])
        expected = performance_cohorts.publication_record_id(record)
        if record["record_id"] != expected:
            raise ValueError(f"Publication record id is not reproducible: expected {expected}")

    expected_observation_id = performance_cohorts.observation_id(observation)
    if observation["observation_id"] != expected_observation_id:
        raise ValueError(
            f"Performance observation id is not reproducible: expected {expected_observation_id}"
        )
    record = next(
        (item for item in records if item["record_id"] == observation["lineage"]["publication_record_id"]),
        None,
    )
    if record is None:
        raise ValueError("Performance observation does not reference the publication registry")
    mirrored = {
        "project_id": record["project_id"],
        "video_id": record["video_id"],
        "publication_id": record["publication_id"],
        "platform": record["platform"],
        "surface": record["surface"],
        "published_at": record["published_at"],
    }
    if any(observation[key] != value for key, value in mirrored.items()):
        raise ValueError("Performance observation identity drifts from publication registry")
    lineage = observation["lineage"]
    if (
        lineage["publication_registry_id"] != registry["registry_id"]
        or lineage["package_id"] != record["package"]["package_id"]
        or lineage["package_sha256"] != record["package"]["sha256"]
        or lineage["target_profile_id"] != record["delivery_check"]["profile_id"]
        or lineage["delivery_sha256"] != record["delivery"]["sha256"]
        or lineage["delivery_check_sha256"] != record["delivery_check"]["sha256"]
        or lineage["verification_status"] != "verified_ready_delivery"
    ):
        raise ValueError("Performance observation lineage drifts from publication evidence")
    expected_tolerance = performance_cohorts.WINDOW_TOLERANCE_HOURS[observation["window_hours"]]
    if observation["window_tolerance_hours"] != expected_tolerance:
        raise ValueError("Performance observation window tolerance drift")
    observation_governance = observation["governance"]
    if (
        observation_governance["causal_claim_allowed"] is not False
        or observation_governance["automatic_rule_promotion"] is not False
        or observation_governance["human_review_required"] is not True
    ):
        raise ValueError("Performance observations must remain non-causal and human-reviewed")

    if store["observations"]:
        raise ValueError("Performance store template must begin empty")
    expected_store_sha = performance_cohorts.canonical_sha256(
        {"store_id": store["store_id"], "observations": store["observations"]}
    )
    if report["source_store_id"] != store["store_id"] or report["source_store_sha256"] != expected_store_sha:
        raise ValueError("Cohort report template is not bound to the performance store template")
    if report["observation_count"] != 0 or report["cohorts"]:
        raise ValueError("Cohort report template must begin without measured cohorts")
    expected_report_id = (
        "COHORT-REPORT-"
        + performance_cohorts.canonical_sha256(
            {
                "source_store_sha256": expected_store_sha,
                "cohort_ids": [],
                "production_record_ids": report["production_record_ids"],
                "analysis_parameters": report["analysis_parameters"],
            }
        )[:16].upper()
    )
    if report["report_id"] != expected_report_id:
        raise ValueError(f"Cohort report id is not reproducible: expected {expected_report_id}")
    report_governance = report["governance"]
    if (
        report_governance["causal_claim_allowed"] is not False
        or report_governance["automatic_rule_promotion"] is not False
        or report_governance["human_interpretation_required"] is not True
        or report_governance["minimum_comparable_publications"] < 3
    ):
        raise ValueError("Cohort reports must remain non-causal and require human interpretation")
    if set(report["analysis_parameters"]["creative_dimensions"]) != set(performance_cohorts.CONTENT_FIELDS):
        raise ValueError("Cohort report must preserve all governed creative dimensions")

    normalized_production = performance_cohorts.normalize_production_record(production)
    return {
        "creative_attribution_id": expected_attribution_id,
        "publication_records": len(records),
        "performance_observations": len(store["observations"]),
        "production_template_id": normalized_production["production_record_id"],
    }


def main():
    paths = {
        "config/radar.json",
        "profiles/default.json",
        "profiles/creative_preferences.json",
        "sources/catalog.json",
        "rules/registry.json",
        "experiments/registry.json",
        "templates/editorial-brief.json",
        "templates/intelligence-decision.json",
        "templates/qa-scorecard.json",
        "library/catalog.json",
        "library/icons/manifest.json",
        "library/sfx/manifest.json",
        "library/music/manifest.json",
        "platforms/catalog.json",
        "styles/catalog.json",
        *SIMPLE_TEMPLATE_SCHEMAS.keys(),
        *SIMPLE_SCHEMA_PATHS,
        *ADVANCED_SCHEMA_PATHS,
    }
    docs = {path: load(path) for path in sorted(paths)}

    # Fail closed if a supposedly simple schema grows beyond the enforced subset.
    for schema_path in sorted(SIMPLE_SCHEMA_PATHS):
        try:
            assert_supported_schema(docs[schema_path])
        except UnsupportedSchemaKeyword as error:
            raise ValueError(f"Simple schema {schema_path} exceeds validator support: {error}") from error
    validate_qa_schema_contract(docs["schemas/qa-scorecard.schema.json"])

    # Real instance validation for every new simple template contract.
    for instance_path, schema_path in SIMPLE_TEMPLATE_SCHEMAS.items():
        require_schema_match(instance_path, docs[instance_path], docs[schema_path])

    if docs["templates/intelligence-decision.json"]["framework_version"] != FRAMEWORK_VERSION:
        raise ValueError("Framework version drift in intelligence-decision template")
    if docs["templates/asset-lock.json"]["framework_version"] != FRAMEWORK_VERSION:
        raise ValueError("Framework version drift in asset-lock template")
    if docs["rules/registry.json"]["framework_version"] != FRAMEWORK_VERSION:
        raise ValueError("Framework version drift in rules registry")

    rule_count = validate_rules(docs["rules/registry.json"], docs["schemas/rule.schema.json"])
    source_ids = {item["id"] for item in docs["sources/catalog.json"]["sources"]}
    source_urls = {item["url"] for item in docs["sources/catalog.json"]["sources"]}
    observations = sorted((ROOT / "research/observations").glob("*.json"))
    for observation_path in observations:
        with observation_path.open(encoding="utf-8") as handle:
            observation = json.load(handle)
        for item in observation.get("platform_changes", []):
            if item["source_id"] not in source_ids:
                raise ValueError(f"Unknown source in {observation_path.name}: {item['source_id']}")

    asset_count = validate_assets(docs["library/catalog.json"], docs["schemas/asset.schema.json"])
    preference_count = validate_preferences(docs["profiles/creative_preferences.json"])
    feedback_count = validate_feedback(docs["schemas/feedback-event.schema.json"])
    style_count = validate_styles(
        docs["styles/catalog.json"],
        docs["schemas/style.schema.json"],
        docs["schemas/motion-style.schema.json"],
    )
    platform_profile_count = validate_platform_profiles(
        docs["platforms/catalog.json"],
        docs["schemas/platform-profile.schema.json"],
        source_urls,
    )
    qa_counts = validate_qa_template(docs["templates/qa-scorecard.json"])
    learning_counts = validate_learning_contracts(
        docs["templates/approval-receipt.json"],
        docs["learning/promotion-policy.v1.json"],
        docs["templates/series-contract.json"],
        [
            docs["master-profiles/editorial-mezzanine-hdr-001.json"],
            docs["master-profiles/social-delivery-sdr-001.json"],
        ],
    )
    template_bank_count = validate_template_bank(
        docs["template-bank/registry.json"],
        docs["schemas/template-bank-registry.schema.json"],
        docs["schemas/approval-receipt.schema.json"],
    )
    asset_intelligence_counts = validate_asset_intelligence_contract(
        docs["templates/asset-index.json"],
        docs["templates/asset-usage-history.json"],
    )
    recipe_counts = validate_recipe_contract(
        docs["creative-recipes/catalog.json"],
        docs["templates/creative-recipe-plan.json"],
    )
    workflow_16_counts = validate_review_and_publish_templates(
        docs["templates/review-packet.json"],
        docs["templates/content-lock-evidence.json"],
        docs["templates/publish-package.json"],
    )
    performance_counts = validate_performance_templates(
        docs["templates/creative-attribution.json"],
        docs["templates/publication-registry.json"],
        docs["templates/performance-observation.json"],
        docs["templates/performance-store.json"],
        docs["templates/performance-cohort-report.json"],
        docs["templates/production-metrics.json"],
    )

    for generated in ("library/CATALOGO.md", "library/catalogo.html"):
        if not (ROOT / generated).is_file():
            raise FileNotFoundError(f"Missing generated catalog: {generated}")

    simple_instance_count = (
        len(SIMPLE_TEMPLATE_SCHEMAS)
        + asset_count
        + rule_count
        + feedback_count
        + style_count * 2
        + platform_profile_count
    )
    print(
        f"OK v{FRAMEWORK_VERSION}: {len(paths)} JSON files, {simple_instance_count} schema-validated instances, "
        f"{rule_count} rules, {len(source_ids)} sources, {asset_count} assets, {style_count} portable styles, "
        f"{platform_profile_count} platform profiles, "
        f"{preference_count} preferences, {feedback_count} feedback events, {len(observations)} observation files, "
        f"{learning_counts['master_profiles']} master profiles, "
        f"{learning_counts['template_families']} template families, "
        f"{template_bank_count} bank templates, "
        f"{recipe_counts['recipe_modules']} recipe modules, "
        f"{recipe_counts['recipe_proposals']} recipe proposals, "
        f"{asset_intelligence_counts['indexed_assets']} template index assets, "
        f"{workflow_16_counts['review_decisions']} review scopes, "
        f"{workflow_16_counts['publish_targets']} publish template targets, "
        f"{performance_counts['publication_records']} publication template records, "
        f"{performance_counts['performance_observations']} stored performance observations, "
        f"QA {qa_counts['hard']['total']} hard gates/{qa_counts['editorial']['total']} editorial criteria"
    )


if __name__ == "__main__":
    main()
